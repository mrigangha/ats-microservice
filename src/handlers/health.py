import logging
import os

from src.services.zoho_auth import get_access_token
from src.utils.response import error, success

logger = logging.getLogger(__name__)


def check(event, context):
    try:
        token = get_access_token()
        token_preview = token[:15] + "..." if token else "none"

        return success(
            {
                "status": "ok",
                "service": "ats-zoho-integration",
                "zoho_url": os.environ.get("ZOHO_BASE_URL", ""),
                "token": token_preview,
            }
        )

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return error(f"Service unhealthy: {str(e)}", 503)
