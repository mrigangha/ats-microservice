import os

import requests

from src.services.zoho_auth import get_access_token

BASE_URL = os.environ.get("ZOHO_BASE_URL", "https://recruit.zoho.in/recruit/v2")


def _headers():
    return {
        "Authorization": f"Zoho-oauthtoken {get_access_token()}",
        "Content-Type": "application/json",
    }


# ── JOBS ─────────────────────────────────────────────────────────────────────


def fetch_all_jobs():
    """Fetch ALL job openings from Zoho, handles pagination internally."""
    all_jobs = []
    page = 1

    while True:
        response = requests.get(
            f"{BASE_URL}/Job_Openings",
            headers=_headers(),
            params={"page": page, "per_page": 200},
            timeout=15,
        )

        if response.status_code == 204:
            break

        if response.status_code != 200:
            raise RuntimeError(
                f"Zoho error {response.status_code}: {response.text[:200]}"
            )

        data = response.json()
        all_jobs.extend(data.get("data", []))

        if not data.get("info", {}).get("more_records", False):
            break

        page += 1

    return all_jobs


# ── CANDIDATES ───────────────────────────────────────────────────────────────


def create_candidate(name, email, phone, resume_url):
    """Create a candidate in Zoho Recruit. Returns the new candidate ID."""

    payload = {
        "Last_Name": name,
        "Email": email,
    }
    if phone:
        payload["Mobile"] = phone
    if resume_url:
        payload["Resume_URL"] = resume_url

    response = requests.post(
        f"{BASE_URL}/Candidates",
        headers=_headers(),
        json={"data": [payload]},
        timeout=15,
    )

    if response.status_code not in (200, 201):
        raise RuntimeError(f"Zoho error {response.status_code}: {response.text[:200]}")

    data = response.json()
    results = data.get("data", [])

    if not results:
        raise RuntimeError("Zoho returned no data after candidate creation")

    result = results[0]

    # Duplicate email — return existing candidate ID instead of crashing
    if result.get("code") == "DUPLICATE_DATA":
        existing_id = result.get("details", {}).get("id")
        if existing_id:
            return str(existing_id)
        raise RuntimeError("Duplicate candidate but no existing ID returned")

    if result.get("status") == "error":
        raise RuntimeError(f"Candidate creation failed: {result.get('message')}")

    return str(result["details"]["id"])


def associate_candidate_to_job(candidate_id, job_id):
    """Associate an existing candidate to a job opening in Zoho."""

    payload = {
        "data": [
            {
                "jobids": [job_id],
                "ids": [candidate_id],
                "comments": "Applied via ATS microservice",
            }
        ]
    }

    response = requests.put(
        f"{BASE_URL}/Candidates/actions/associate",
        headers=_headers(),
        json=payload,
        timeout=15,
    )

    if response.status_code not in (200, 201, 204):
        raise RuntimeError(
            f"Association failed {response.status_code}: {response.text[:200]}"
        )

    data = response.json()
    result = data.get("data", [{}])[0]

    if result.get("code") in ("SUCCESS", "ALREADY_ASSOCIATED"):
        return True

    raise RuntimeError(f"Association failed: {result.get('message')}")


# ── APPLICATIONS ─────────────────────────────────────────────────────────────


def fetch_all_applications(job_id):
    """
    Fetch ALL candidates associated to a job opening.
    Uses GET /Job_Openings/{job_id}/associate endpoint.
    Handles pagination internally.
    """
    all_apps = []
    page = 1

    while True:
        response = requests.get(
            f"{BASE_URL}/Job_Openings/{job_id}/associate",
            headers=_headers(),
            params={"page": page, "per_page": 200},
            timeout=15,
        )

        if response.status_code == 204:
            break

        if response.status_code == 404:
            raise RuntimeError(f"Job {job_id} not found")

        if response.status_code != 200:
            raise RuntimeError(
                f"Zoho error {response.status_code}: {response.text[:200]}"
            )

        data = response.json()
        all_apps.extend(data.get("data", []))

        if not data.get("info", {}).get("more_records", False):
            break

        page += 1

    return all_apps


def fetch_all_candidates():
    """Fetch ALL candidates across all jobs, handles pagination internally."""
    all_candidates = []
    page = 1

    while True:
        response = requests.get(
            f"{BASE_URL}/Candidates",
            headers=_headers(),
            params={"page": page, "per_page": 200},
            timeout=15,
        )

        if response.status_code == 204:
            break

        if response.status_code != 200:
            raise RuntimeError(
                f"Zoho error {response.status_code}: {response.text[:200]}"
            )

        data = response.json()
        all_candidates.extend(data.get("data", []))

        if not data.get("info", {}).get("more_records", False):
            break

        page += 1

    return all_candidates
