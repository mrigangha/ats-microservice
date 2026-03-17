import logging

from src.services.zoho_service import fetch_all_applications, fetch_all_candidates
from src.utils.response import error, normalize_application, success

logger = logging.getLogger(__name__)


def get_applications(event, context):
    try:
        params = event.get("queryStringParameters") or {}
        job_id = params.get("job_id", "").strip()

        if job_id:
            raw = fetch_all_applications(job_id)
            applications = [normalize_application(a) for a in raw]
            return success(
                {
                    "applications": applications,
                    "total": len(applications),
                    "job_id": job_id,
                }
            )
        else:
            raw = fetch_all_candidates()
            applications = [normalize_application(a) for a in raw]
            return success(
                {
                    "applications": applications,
                    "total": len(applications),
                }
            )

    except RuntimeError as e:
        logger.error(f"Zoho API error: {e}")
        return error(str(e), 502)

    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return error("Internal server error", 500)
