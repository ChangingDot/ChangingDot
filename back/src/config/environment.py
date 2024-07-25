import os

from dotenv import load_dotenv

load_dotenv()


ANAYLZER_URL = (
    os.environ.get("ANALYZER_URL")
    if os.environ.get("ANALYZER_URL") is not None
    else "localhost:5177"
)


QUEUE_CONFIG = {
    "host": os.environ.get("REDIS_HOST"),
    "port": os.environ.get("REDIS_PORT", 6379),
    "password": os.environ.get("REDIS_PASSWORD", None),
    "db": os.environ.get("REDIS_DB", 1),
}

GCS_BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME")

GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
