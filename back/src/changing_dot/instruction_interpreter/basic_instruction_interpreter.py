import os

from changing_dot.custom_types import Edits, Instruction
from changing_dot.instruction_interpreter.instruction_interpreter import (
    IInstructionInterpreter,
)
from changing_dot.instruction_interpreter.prompts import (
    one_liner_edits_template,
    system_prompt,
)
from changing_dot.utils.text_functions import read_text
from changing_dot_visualize.observer import Observer
from dotenv import load_dotenv
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_mistralai import ChatMistralAI
from langchain_openai import ChatOpenAI
from pydantic.v1.types import SecretStr


def create_mistral_interpreter(observer: Observer) -> IInstructionInterpreter:
    load_dotenv()
    mistral_api_key = SecretStr(os.getenv("MISTRAL_API_KEY") or "")
    return BasicInstructionInterpreter(
        ChatMistralAI(mistral_api_key=mistral_api_key, model="mistral-large-latest"),
        observer,
    )


def create_openai_interpreter(observer: Observer) -> IInstructionInterpreter:
    load_dotenv()
    return BasicInstructionInterpreter(ChatOpenAI(model="gpt-4-1106-preview"), observer)


class BasicInstructionInterpreter(IInstructionInterpreter):
    model: BaseChatModel
    observer: Observer | None

    def __init__(self, model: BaseChatModel, observer: Observer | None = None):
        self.model = model
        self.observer = observer

    def get_edits_from_instruction(self, instruction: Instruction) -> Edits:
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", one_liner_edits_template),
            ]
        )
        chain = prompt | self.model | StrOutputParser()

        file_content = read_text(instruction["file_path"])
        if not file_content.endswith("\n"):
            file_content = file_content + "\n"
        lines = file_content.splitlines(keepends=True)

        line_content = lines[instruction["line_number"] - 1]

        output = chain.invoke(
            {
                "programming_language": instruction["programming_language"],
                "error": instruction["error"],
                "solution": instruction["solution"],
                "file_name": instruction["file_path"].split("/")[-1],
                "content": line_content,
            }
        )

        if self.observer:
            self.observer.log(f"Got from openai the following response : {output}")

        before, after = process_output(output)

        if self.observer:
            self.observer.log(f"Got before, after {before}, {after}")

        if len(before) == 0 and len(after) == 0:
            return []

        edit_type = instruction["edit_type"]
        if edit_type == "replace":
            if len(after) == 0:
                return [
                    {
                        "edit_type": "remove",
                        "file_path": instruction["file_path"],
                        "line_number": instruction["line_number"],
                        "line_to_remove": before[-1],
                    }
                ]
            if len(before) == 0:
                return [
                    {
                        "edit_type": "add",
                        "file_path": instruction["file_path"],
                        "line_number": instruction["line_number"],
                        "line_to_add": after[-1],
                    }
                ]
            return [
                {
                    "edit_type": "replace",
                    "file_path": instruction["file_path"],
                    "line_number": instruction["line_number"],
                    "before": before[-1],
                    "after": after[-1],
                }
            ]
        if edit_type == "add":
            return [
                {
                    "edit_type": "add",
                    "file_path": instruction["file_path"],
                    "line_number": instruction["line_number"],
                    "line_to_add": after[-1],
                }
            ]
        if edit_type == "remove":
            return [
                {
                    "edit_type": "remove",
                    "file_path": instruction["file_path"],
                    "line_number": instruction["line_number"],
                    "line_to_remove": before[-1],
                }
            ]
        raise ValueError(f"Unexpected edit type - {edit_type}")


def process_output(output: str) -> tuple[list[str], list[str]]:
    if not output.endswith("\n"):
        output = output + "\n"

    lines = output.splitlines(keepends=True)

    line_num = 0
    all_edits = []

    while line_num < len(lines):
        line = lines[line_num]

        # start processing llm response if start of a diff block, else pass
        if line.startswith("```diff"):
            start_line_num = line_num + 1
            edits = get_edits_from_diff_block(lines, start_line_num)

            all_edits += edits

        line_num += 1

    before, after = edits_to_before_after(all_edits)

    return before, after


def get_edits_from_diff_block(lines: list[str], start_line_num: int) -> list[str]:
    end_line_num = start_line_num

    # get end line number of diff block
    for line_num in range(start_line_num, len(lines)):
        end_line_num = line_num

        line = lines[line_num]
        if line.startswith("```"):
            break

    block = lines[start_line_num:end_line_num]
    block.append("@@ @@")

    if block[0].startswith("--- ") and block[1].startswith("+++ "):
        # Remove the file path, because we already have it
        block = block[2:]

    edits: list[str] = []

    keeper = False
    hunk = []
    op = " "
    for line in block:
        hunk.append(line)
        if len(line) < 2:
            continue

        if line.startswith("+++ ") and hunk[-2].startswith("--- "):
            hunk = hunk[:-3] if hunk[-3] == "\n" else hunk[:-2]
            edits += hunk
            hunk = []
            keeper = False

            continue

        op = line[0]
        if op in "-+":
            keeper = True
            continue
        if op != "@":
            continue
        if not keeper:
            hunk = []
            continue

        hunk = hunk[:-1]
        edits += hunk
        hunk = []
        keeper = False

    return edits


def edits_to_before_after(hunk: list[str]) -> tuple[list[str], list[str]]:
    before = []
    after = []
    op = " "
    for line in hunk:
        if len(line) < 2:
            op = " "
            line = line
        else:
            op = line[0]
            line = line[1:]
        if op == "-":
            before.append(line)
        elif op == "+":
            after.append(line)

    for line in before:
        if line in after:
            before.remove(line)
            after.remove(line)

    return before, after
