import json
import time
from uuid import UUID

import redis

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.dataset import Dataset
from app.models.dataset_analysis import DatasetAnalysis
from app.services.analysis_service import run_analysis_job


ANALYSIS_QUEUE = "analysis_jobs"


def get_redis_client() -> redis.Redis:
    """
    Create a Redis client for the analysis worker.

    The socket timeout is disabled because the worker
    intentionally uses BRPOP as a blocking queue operation.
    """

    return redis.from_url(
        settings.redis_url,
        decode_responses=True,
        socket_timeout=None,
        socket_connect_timeout=5,
        health_check_interval=30,
    )


def process_analysis_job(
    job: dict,
) -> None:
    """
    Process a single analysis job received from Redis.
    """

    analysis_id = UUID(
        job["analysis_id"]
    )

    db = SessionLocal()

    try:
        analysis = (
            db.query(DatasetAnalysis)
            .filter(
                DatasetAnalysis.id
                == analysis_id
            )
            .first()
        )

        if analysis is None:
            return

        dataset = (
            db.query(Dataset)
            .filter(
                Dataset.id
                == analysis.dataset_id
            )
            .first()
        )

        if dataset is None:
            analysis.status = "failed"
            analysis.error_message = (
                "Dataset not found."
            )
            db.commit()
            return

        storage_path = (
            job["storage_path"]
        )

        run_analysis_job(
            db=db,
            analysis=analysis,
            dataset=dataset,
            storage_path=storage_path,
        )

    except Exception:
        db.rollback()

        analysis = (
            db.query(DatasetAnalysis)
            .filter(
                DatasetAnalysis.id
                == analysis_id
            )
            .first()
        )

        if analysis is not None:
            analysis.status = "failed"
            analysis.error_message = (
                "Dataset analysis failed."
            )
            db.commit()

    finally:
        db.close()


def run_worker() -> None:
    """
    Continuously process analysis jobs
    from the Redis queue.
    """

    redis_client = (
        get_redis_client()
    )

    print(
        "Analysis worker started."
    )

    while True:

        try:
            job_item = (
                redis_client.brpop(
                    ANALYSIS_QUEUE,
                    timeout=5,
                )
            )

            if job_item is None:
                continue

            _, job_data = job_item

            job = json.loads(
                job_data
            )

            process_analysis_job(
                job
            )

        except KeyboardInterrupt:

            print(
                "Analysis worker stopped."
            )
            break

        except Exception as exc:

            print(
                "Worker error:",
                str(exc),
            )

            time.sleep(2)


if __name__ == "__main__":
    run_worker()