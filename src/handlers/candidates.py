import json
import logging

from src.services.zoho_service import associate_candidate_to_job
from src.services.zoho_service import create_candidate as zoho_create_candidate
from src.utils.response import error, success

logger = logging.getLogger(__name__)

REQUIRED_FIELDS = ["name", "email", "job_id"]


def create_candidate(event, context):
    """
    POST /candidates
    Creates a candidate in Zoho Recruit and attaches them to a job.

    Request body:
    {
        "name":       "John Doe",         required
        "email":      "john@gmail.com",   required
        "phone":      "+91 9876543210",   optional
        "resume_url": "https://...",      optional
        "job_id":     "576753000000123"   required
    }
    """
    try:
        try:
            body = json.loads(event.get("body") or "{}")
        except json.JSONDecodeError:
            return error("Invalid JSON body", 400)

        missing = [f for f in REQUIRED_FIELDS if not body.get(f)]
        if missing:
            return error(f"Missing required fields: {', '.join(missing)}", 400)

        name = body["name"].strip()
        email = body["email"].strip()
        phone = body.get("phone", "").strip()
        resume_url = body.get("resume_url", "").strip()
        job_id = body["job_id"].strip()

        candidate_id = zoho_create_candidate(name, email, phone, resume_url)
        logger.info(f"Created candidate {candidate_id} in Zoho")

        # ── Step 2: Associate candidate to job ────────────────────
        associate_candidate_to_job(candidate_id, job_id)
        logger.info(f"Associated candidate {candidate_id} to job {job_id}")

        return success(
            {
                "message": "Candidate created successfully",
                "candidate_id": candidate_id,
                "job_id": job_id,
            },
            201,
        )

    except RuntimeError as e:
        logger.error(f"Zoho API error: {e}")
        return error(str(e), 502)

    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return error("Internal server error", 500)
