from typing import Literal

from changing_dot.custom_types import BlockEdit, EmptyEdit, InstructionBlock
from changing_dot.dependency_graph.dependency_graph import DependencyGraph
from changing_dot.instruction_interpreter.block_prompts import (
    edits_template,
    system_prompt,
)
from changing_dot.instruction_interpreter.instruction_interpreter import (
    IBlockInstructionInterpreter,
)
from changing_dot.utils.llm_model_utils import get_mistral_api_key
from changing_dot.utils.text_functions import extract_code_blocks
from changing_dot_visualize.observer import Observer
from dotenv import load_dotenv
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import (
    RunnableSerializable,
)
from langchain_mistralai import ChatMistralAI
from langchain_openai import ChatOpenAI


class BlockInstructionInterpreter(IBlockInstructionInterpreter):
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

    def get_edit_from_instruction(
        self, instruction: InstructionBlock, DG: DependencyGraph
    ) -> BlockEdit:
        before_node = DG.get_node(instruction["block_id"])
        before = before_node.text

        chain = self.make_chain()

        output = chain.invoke({"solution": instruction["solution"], "content": before})

        if self.observer:
            self.observer.log(f"Got from LLM the following response : {output}")

        code_blocks = extract_code_blocks(output)

        if len(code_blocks) == 0:
            return EmptyEdit(
                block_id=instruction["block_id"],
                file_path=instruction["file_path"],
            )

        code_block = code_blocks[-1]

        # Check indentation
        if len(before.splitlines()) > 1:
            existing_indentation = before_node.start_point[1]
            generated_indentation = len(code_block.splitlines()[0]) - len(
                code_block.splitlines()[0].lstrip()
            )

            if generated_indentation != existing_indentation:
                non_indented_lines = code_block.splitlines()
                indented_lines = []
                # add existing indentation to all lines but first
                for line in non_indented_lines:
                    if line != "":
                        line = " " * existing_indentation + line
                    indented_lines.append(line)

                code_block = "\n".join(indented_lines)

        code_block = code_block.lstrip()

        if code_block.endswith("\n"):
            code_block = code_block[:-1]

        return BlockEdit(
            block_id=instruction["block_id"],
            file_path=instruction["file_path"],
            before=before,
            after=code_block,
        )


def create_instruction_interpreter(
    observer: Observer,
    llm_provider: Literal["OPENAI", "MISTRAL"],
) -> BlockInstructionInterpreter:
    load_dotenv()
    if llm_provider == "OPENAI":
        openai_chat: BaseChatModel = ChatOpenAI(model="gpt-4o", temperature=0.0)
        return BlockInstructionInterpreter(model=openai_chat, observer=observer)
    elif llm_provider == "MISTRAL":
        mistral_api_key = get_mistral_api_key()
        mistral_chat: BaseChatModel = ChatMistralAI(
            mistral_api_key=mistral_api_key,
            model="mistral-large-latest",
            temperature=0.0,
        )
        return BlockInstructionInterpreter(model=mistral_chat, observer=observer)
