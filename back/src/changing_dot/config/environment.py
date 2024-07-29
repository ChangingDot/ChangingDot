import os

from dotenv import load_dotenv

load_dotenv()


ANAYLZER_URL = (
    os.environ.get("ANALYZER_URL")
    if os.environ.get("ANALYZER_URL") is not None
    else "localhost:5177"
)
