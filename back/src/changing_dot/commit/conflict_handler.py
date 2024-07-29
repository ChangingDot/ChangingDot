import os
import re

from changing_dot_visualize.observer import Observer
from dotenv import load_dotenv
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_mistralai import ChatMistralAI
from langchain_openai import ChatOpenAI
from pydantic.v1.types import SecretStr


def extract_code_blocks(text: str) -> str:
    code_block_pattern = r"```(?:\w+\n)?(.*?)```"
    code_blocks = re.findall(code_block_pattern, text, re.DOTALL)
    if len(code_blocks) == 0:
        return ""
    return str(code_blocks[0])


system_prompt = """You are an expert software engineer. Your role is to help me fix merge conflicts. Can plaese respond with the whole files content with the conflict resolved"""

prompt = """Can you fix me the following conflict : {file_content}"""


class ConflictHandler:
    model: BaseChatModel
    observer: Observer | None

    def __init__(
        self,
        model: BaseChatModel,
        observer: Observer | None = None,
    ):
        self.model = model
        self.observer = observer

    def handle_conflict(self, file_content: str) -> str:
        conflict_handler_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", prompt),
            ]
        )

        task = {"file_content": file_content}
        chain = conflict_handler_prompt | self.model | StrOutputParser()

        output = chain.invoke(task)
        result = extract_code_blocks(output)
        return result


def create_openai_conflict_handler() -> ConflictHandler:
    load_dotenv()

    chat = ChatOpenAI(model="gpt-4-1106-preview", temperature=0.0)

    return ConflictHandler(model=chat)


def create_mistral_conflict_handler() -> ConflictHandler:
    load_dotenv()
    mistral_api_key = SecretStr(os.getenv("MISTRAL_API_KEY") or "")
    chat = ChatMistralAI(mistral_api_key=mistral_api_key, model="mistral-large-latest")
    return ConflictHandler(model=chat)
