import json


def success(body, status_code=200):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }


def error(message, status_code=500):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"error": message}),
    }


JOB_STATUS_MAP = {
    "In-progress": "OPEN",
    "Authorised": "OPEN",
    "Filled": "CLOSED",
    "Closed": "CLOSED",
    "Cancelled": "CLOSED",
    "Draft": "DRAFT",
    "Approval Pending": "DRAFT",
}

APP_STATUS_MAP = {
    "New": "APPLIED",
    "In-Review": "SCREENING",
    "Available": "SCREENING",
    "Engaged": "SCREENING",
    "Offered": "SCREENING",
    "Hired": "HIRED",
    "Rejected": "REJECTED",
    "Unqualified": "REJECTED",
}


def normalize_job(job):
    city = job.get("City") or ""
    state = job.get("State") or ""
    country = job.get("Country") or ""
    parts = [p for p in [city, state, country] if p]
    location = ", ".join(parts) if parts else "Remote"

    raw_status = job.get("Job_Status", "")
    status = JOB_STATUS_MAP.get(raw_status, "DRAFT")

    return {
        "id": str(job.get("id", "")),
        "title": job.get("Job_Opening_Name", ""),
        "location": location,
        "status": status,
        "external_url": job.get("Job_Opening_URL") or "",
    }


def normalize_application(app):
    raw_status = app.get("Candidate_Status", "New")
    status = APP_STATUS_MAP.get(raw_status, "APPLIED")

    return {
        "id": str(app.get("id", "")),
        "candidate_name": app.get("Full_Name") or app.get("Last_Name", ""),
        "email": app.get("Email", ""),
        "status": status,
    }
