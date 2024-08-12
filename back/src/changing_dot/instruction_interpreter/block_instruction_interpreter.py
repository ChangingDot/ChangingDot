from changing_dot.custom_types import BlockEdit, EmptyEdit, InstructionBlock
from changing_dot.dependency_graph.dependency_graph import DependencyGraph
from changing_dot.instruction_interpreter.block_prompts import (
    edits_template,
    system_prompt,
)
from changing_dot.instruction_interpreter.instruction_interpreter import (
    IBlockInstructionInterpreter,
)
from changing_dot.utils.process_diff import process_diff
from changing_dot_visualize.observer import Observer
from dotenv import load_dotenv
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import (
    RunnableSerializable,
)
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
        before = DG.get_node(instruction["block_id"]).text

        chain = self.make_chain()

        output = chain.invoke({"solution": instruction["solution"], "content": before})

        if self.observer:
            self.observer.log(f"Got from LLM the following response : {output}")

        processed_outputs = process_diff(output, before)

        if len(processed_outputs) == 0:
            return EmptyEdit(
                block_id=instruction["block_id"],
                file_path=instruction["file_path"],
            )

        after = before
        for processed_output in processed_outputs:
            processed_output.before = processed_output.before.lstrip()
            processed_output.after = processed_output.after.lstrip()

            if processed_output.before.strip() == "":
                raise ValueError("Code was added, but we do not know where to put it")

            if processed_output.before not in after:
                if self.observer:
                    self.observer.log(
                        f"Error : Could not replace {processed_output.before} in {after}"
                    )

            after = after.replace(processed_output.before, processed_output.after)

        return BlockEdit(
            block_id=instruction["block_id"],
            file_path=instruction["file_path"],
            before=before,
            after=after,
        )


def create_openai_interpreter(observer: Observer) -> BlockInstructionInterpreter:
    load_dotenv()
    return BlockInstructionInterpreter(
        ChatOpenAI(model="gpt-4o", temperature=0.0), observer
    )
