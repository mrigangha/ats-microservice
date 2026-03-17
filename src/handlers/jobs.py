import logging

from src.services.zoho_service import fetch_all_jobs
from src.utils.response import error, normalize_job, success

logger = logging.getLogger(__name__)


def get_jobs(event, context):
    """
    GET /jobs
    Returns all job openings from Zoho Recruit.

    Optional query param:
      ?status=OPEN|CLOSED|DRAFT  → filter by status
    """
    try:
        params = event.get("queryStringParameters") or {}
        status_filter = params.get("status", "").upper()

        raw_jobs = fetch_all_jobs()
        logger.info(f"Fetched {len(raw_jobs)} jobs from Zoho")

        jobs = [normalize_job(j) for j in raw_jobs]

        if status_filter in ("OPEN", "CLOSED", "DRAFT"):
            jobs = [j for j in jobs if j["status"] == status_filter]

        return success(
            {
                "jobs": jobs,
                "total": len(jobs),
            }
        )

    except RuntimeError as e:
        logger.error(f"Zoho API error: {e}")
        return error(str(e), 502)

    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return error("Internal server error", 500)
