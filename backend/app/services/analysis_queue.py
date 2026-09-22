import json

import redis

from app.core.config import settings


ANALYSIS_QUEUE = "analysis_jobs"


def get_redis_client() -> redis.Redis:
    """
    Create a Redis client for queue operations.
    """

    return redis.from_url(
        settings.redis_url,
        decode_responses=True,
    )


def enqueue_analysis_job(
    analysis_id: str,
    storage_path: str,
) -> None:
    """
    Add an analysis job to the Redis queue.
    """

    redis_client = get_redis_client()

    job = {
        "analysis_id": analysis_id,
        "storage_path": storage_path,
    }

    redis_client.lpush(
        ANALYSIS_QUEUE,
        json.dumps(job),
    )