import logging
import re


def read_text(filename: str) -> str:
    encoding = "utf-8-sig"

    try:
        with open(str(filename), encoding=encoding) as f:
            return f.read()
    except FileNotFoundError:
        logging.error(f"{filename}: file not found error")
        raise FileNotFoundError from None
    except IsADirectoryError:
        logging.error(f"{filename}: is a directory")
        raise IsADirectoryError from None
    except UnicodeError as e:
        logging.error(f"{filename}: {e} \n Use --encoding to set the unicode encoding.")
        raise UnicodeError from None


def write_text(filename: str, content: str) -> None:
    encoding = "utf-8"
    with open(str(filename), "w", encoding=encoding) as f:
        f.write(content)


def extract_code_blocks(text: str) -> list[str]:
    pattern = r"```(?:\w+)?\n([\s\S]*?)\n```"
    return re.findall(pattern, text)
