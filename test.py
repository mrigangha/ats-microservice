import requests

# ── Fill your credentials ────────────────────────────────────────
CLIENT_ID = "1000.KWFM6REAXLTLGHV3T4GSYVGT1UMRZG"
CLIENT_SECRET = "5d8da95a805bed8c768ef0fae44eb5d632e4fcd8cb"
REFRESH_TOKEN = "1000.34edb76306ab073997a5377f17ca33fb.18d32a69fb436abb458a568a69ee15c4"
ACCOUNTS_URL = "https://accounts.zoho.in"
BASE_URL = "https://recruit.zoho.in/recruit/v2"
JOB_ID = "214960000000367958"

# ── Get token ────────────────────────────────────────────────────
resp = requests.post(
    f"{ACCOUNTS_URL}/oauth/v2/token",
    params={
        "refresh_token": REFRESH_TOKEN,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token",
    },
)
token = resp.json()["access_token"]
headers = {
    "Authorization": f"Zoho-oauthtoken {token}",
    "Content-Type": "application/json",
}

# ── Try all possible endpoints ───────────────────────────────────

print("=" * 60)
print("Try 1: Job_Openings/{id}/Candidates (GET)")
r = requests.get(f"{BASE_URL}/Job_Openings/{JOB_ID}/Candidates", headers=headers)
print(f"Status: {r.status_code}")
print(f"Body:   {r.text[:400]}")

print("\n" + "=" * 60)
print("Try 2: Job_Applications module")
r = requests.get(
    f"{BASE_URL}/Job_Applications",
    headers=headers,
    params={"criteria": f"(Job_Opening_Id:equals:{JOB_ID})"},
)
print(f"Status: {r.status_code}")
print(f"Body:   {r.text[:400]}")

print("\n" + "=" * 60)
print("Try 3: Candidates/search by word")
r = requests.get(
    f"{BASE_URL}/Candidates/search", headers=headers, params={"word": "John"}
)
print(f"Status: {r.status_code}")
print(f"Body:   {r.text[:400]}")

print("\n" + "=" * 60)
print("Try 4: Job_Openings/{id}/Candidates with page param")
r = requests.get(
    f"{BASE_URL}/Job_Openings/{JOB_ID}/Candidates",
    headers=headers,
    params={"page": 1, "per_page": 10},
)
print(f"Status: {r.status_code}")
print(f"Body:   {r.text[:400]}")
