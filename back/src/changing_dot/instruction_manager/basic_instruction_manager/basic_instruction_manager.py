import os
from typing import Literal

from changing_dot.changing_graph.changing_graph import ChangingGraph
from changing_dot.custom_types import Instruction, edit_to_diff
from changing_dot.instruction_manager.basic_instruction_manager.prompt import (
    make_format_prompt,
    prompt,
    system_prompt,
)
from changing_dot.instruction_manager.instruction_manager import IInstructionManager
from changing_dot.instruction_manager.prompt_diff import create_prompt_diff_block
from dotenv import load_dotenv
from langchain.chains.base import Chain
from langchain.prompts import PromptTemplate
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel
from langchain_core.runnables import RunnablePassthrough
from langchain_mistralai import ChatMistralAI
from langchain_openai import ChatOpenAI
from pydantic.v1.types import SecretStr


class IntructionOutputModel(BaseModel):
    edit_type: Literal["replace"] | Literal["add"] | Literal["remove"]
    line_number: int
    solution: str


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


class BasicInstructionManager(IInstructionManager):
    model: BaseChatModel
    json_model: BaseChatModel
    goal: str

    def __init__(self, model: BaseChatModel, json_model: BaseChatModel, goal: str):
        self.model = model
        self.json_model = json_model
        self.goal = goal

    def get_node_instruction(self, G: ChangingGraph, node_index: int) -> Instruction:
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

        output = chain.invoke(task)

        return {
            "edit_type": output["edit_type"].lower(),
            "programming_language": "c#",
            "file_path": error["file_path"],
            "line_number": output["line_number"],
            "error": error["text"],
            "solution": output["solution"],
        }

    def make_chain(self) -> Chain:
        instruction_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", prompt),
            ]
        )

        instruction_chain = instruction_prompt | self.model | StrOutputParser()

        output_parser = JsonOutputParser(pydantic_object=IntructionOutputModel)

        jsonify_chain = (
            {"data": RunnablePassthrough()}  # type: ignore
            | PromptTemplate(
                template="Can you format this data ? {format_instructions} {data}",
                input_variables=["data"],
                partial_variables={
                    "format_instructions": make_format_prompt("replace, add, remove")
                },
            )
            | self.json_model
            | output_parser
        )

        chain = instruction_chain | jsonify_chain
        return chain  # type: ignore


def create_openai_instruction_manager(goal: str) -> BasicInstructionManager:
    load_dotenv()

    chat = ChatOpenAI(model="gpt-4-1106-preview", temperature=0.0)
    json_chat = ChatOpenAI(
        model="gpt-3.5-turbo-1106",
        temperature=0.0,
        response_format={"type": "json_object"},  # type: ignore
    )
    return BasicInstructionManager(model=chat, json_model=json_chat, goal=goal)


def create_mistral_instruction_manager(goal: str) -> BasicInstructionManager:
    load_dotenv()
    mistral_api_key = SecretStr(os.getenv("MISTRAL_API_KEY") or "")
    chat = ChatMistralAI(mistral_api_key=mistral_api_key, model="mistral-large-latest")
    json_chat = ChatMistralAI(
        mistral_api_key=mistral_api_key, model="mistral-large-latest"
    )
    return BasicInstructionManager(model=chat, json_model=json_chat, goal=goal)
