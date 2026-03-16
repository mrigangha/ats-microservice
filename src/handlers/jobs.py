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
        # Read optional status filter from query params
        params = event.get("queryStringParameters") or {}
        status_filter = params.get("status", "").upper()

        # Fetch all jobs from Zoho (pagination handled inside)
        raw_jobs = fetch_all_jobs()
        logger.info(f"Fetched {len(raw_jobs)} jobs from Zoho")

        # Normalize to our unified format
        jobs = [normalize_job(j) for j in raw_jobs]

        # Apply optional status filter
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
