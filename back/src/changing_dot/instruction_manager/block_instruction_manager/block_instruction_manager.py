from typing import TypedDict

from changing_dot.changing_graph.changing_graph import ChangingGraph
from changing_dot.custom_types import edit_to_diff
from changing_dot.dependency_graph.dependency_graph import DependencyGraph
from changing_dot.instruction_manager.block_instruction_manager.prompt import (
    prompt,
    system_prompt,
)
from changing_dot.instruction_manager.prompt_diff import create_prompt_diff_block
from dotenv import load_dotenv
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.output_parsers import (
    BaseOutputParser,
)
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import (
    RunnableSerializable,
)
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, ValidationError


class InstructionOutput(BaseModel):
    block_id: int
    instructions: str


class InstructionOutputParser(BaseOutputParser[InstructionOutput]):
    def parse(self, text: str) -> InstructionOutput:
        try:
            lines = text.split("\n")
            block_id_line = lines[0].strip()
            instructions_lines = lines[1:]

            block_id = int(block_id_line.split(": ")[1])

            instructions = "\n".join(
                line.split(": ", 1)[1] if ": " in line else line
                for line in instructions_lines
            ).strip()

            return InstructionOutput(block_id=block_id, instructions=instructions)
        except (IndexError, ValueError, ValidationError) as e:
            raise ValueError(f"Error parsing output: {e}") from e


class InstructionBlock(TypedDict):
    block_id: int
    file_path: str
    solution: str


class IInstructionManagerBlock:
    def get_node_instruction(
        self, G: ChangingGraph, DG: DependencyGraph, node_index: int
    ) -> InstructionBlock:
        raise NotImplementedError()


def get_failed_attempts(G: ChangingGraph, node_index: int) -> str:
    failed_attempt_nodes = G.get_failed_solution_to_problem(node_index)
    if len(failed_attempt_nodes) == 0:
        return ""

    attempt_diffs = [
        f"Attempt {i}\n{edit_to_diff(edit)}\n"
        for i, node in enumerate(failed_attempt_nodes)
        for edit in node["edits"]
    ]

    return f"We have already tried this, but it did not fix the error : {attempt_diffs}"


class BlockInstructionManager(IInstructionManagerBlock):
    def __init__(self, model: BaseChatModel, goal: str):
        self.model = model
        self.goal = goal

    def get_node_instruction(
        self, G: ChangingGraph, DG: DependencyGraph, node_index: int
    ) -> InstructionBlock:
        chain = self.make_chain()

        # get relevant error node
        problem_node = G.get_node(node_index)
        assert problem_node["node_type"] == "problem"
        error = problem_node["error"]

        if node_index == 0:
            edits = []
        else:
            # get solution that caused that problem
            solution_parent_node_indexes = G.get_parent_nodes(node_index)
            # all problems need to have a solution that caused it
            assert len(solution_parent_node_indexes) > 0
            # TODO what do we do if many problems caused the same problem ?
            # -> for now take first
            solution_node = G.get_node(solution_parent_node_indexes[0])
            assert solution_node["node_type"] == "solution"
            edits = solution_node["edits"]

        # get global objective
        root_node = G.get_node(0)
        assert root_node["node_type"] == "problem"

        prompt_diff = create_prompt_diff_block(error, edits)

        failed_attempts = get_failed_attempts(G, node_index)

        task = {
            "goal": self.goal,
            "prompt_diff": prompt_diff,
            "failed_attempts": failed_attempts,
        }

        output: InstructionOutput = chain.invoke(task)

        return {
            "block_id": 1,
            "file_path": error["file_path"],
            "solution": output.instructions,
        }

    def make_chain(self) -> RunnableSerializable[dict[str, str], InstructionOutput]:
        instruction_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", prompt),
            ]
        )

        instruction_chain = instruction_prompt | self.model | InstructionOutputParser()

        return instruction_chain


def create_openai_instruction_manager(goal: str) -> BlockInstructionManager:
    load_dotenv()
    chat = ChatOpenAI(model="gpt-4o", temperature=0.0)
    return BlockInstructionManager(model=chat, goal=goal)
