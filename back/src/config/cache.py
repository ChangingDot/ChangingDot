import os

from redis import Redis, StrictRedis
from rq import Queue

from config.environment import QUEUE_CONFIG

REDIS_URL = os.environ.get("REDIS_URL")

cache = StrictRedis(
    host=QUEUE_CONFIG["host"],
    port=QUEUE_CONFIG["port"],
    password=QUEUE_CONFIG["password"],
    db=QUEUE_CONFIG["db"],
)

broker = Redis(
    host=QUEUE_CONFIG["host"],
    port=QUEUE_CONFIG["port"],
    password=QUEUE_CONFIG["password"],
    db=QUEUE_CONFIG["db"],
)

queue = Queue(connection=broker, default_timeout=7200)
