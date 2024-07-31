from changing_dot.dependency_graph.dependency_graph import DependencyGraph
from changing_dot.instruction_interpreter.block_prompts import (
    edits_template,
    system_prompt,
)
from changing_dot.instruction_manager.block_instruction_manager.block_instruction_manager import (
    InstructionBlock,
)
from changing_dot_visualize.observer import Observer
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import (
    RunnableSerializable,
)
from pydantic import BaseModel


class BlockEdit(BaseModel):
    file_path: str
    block_id: int
    before: str
    after: str


class BlockInstructionInterpreter:
    def __init__(self, model: BaseChatModel, observer: Observer | None = None):
        self.model = model
        self.observer = observer

    def make_chain(self) -> RunnableSerializable[dict[str, str], str]:
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", edits_template),
            ]
        )
        return prompt | self.model | StrOutputParser()

    def get_edits_from_instruction(
        self, instruction: InstructionBlock, DG: DependencyGraph
    ) -> list[BlockEdit]:
        before = DG.get_node(instruction["block_id"]).text
        chain = self.make_chain()

        output = chain.invoke({"solution": instruction["solution"], "content": before})

        if self.observer:
            self.observer.log(f"Got from LLM the following response : {output}")

        after = process_output(output)

        if after == "":
            return []

        return [
            BlockEdit(
                block_id=instruction["block_id"],
                file_path=instruction["file_path"],
                before=before,
                after=after,
            )
        ]


def process_output(output: str) -> str:
    if not output.endswith("\n"):
        output = output + "\n"

    lines = output.splitlines(keepends=True)
    plus_lines = [
        line[1:]
        for line in lines
        if line.strip().startswith("+") and not line.strip().startswith("+++")
    ]

    return "".join(plus_lines)
