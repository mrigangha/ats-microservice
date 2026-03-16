import os
import time

import requests

# Simple in-memory cache
_token_cache = {
    "access_token": None,
    "expires_at": 0,
}


def get_access_token():
    """Return valid access token, refresh if expired."""
    now = time.time()

    # Return cached token if still valid
    if _token_cache["access_token"] and now < _token_cache["expires_at"] - 60:
        return _token_cache["access_token"]

    return _refresh_token()


def _refresh_token():
    """Call Zoho to get a new access token using refresh token."""
    url = f"{os.environ['ZOHO_ACCOUNTS_URL']}/oauth/v2/token"

    params = {
        "refresh_token": os.environ["ZOHO_REFRESH_TOKEN"],
        "client_id": os.environ["ZOHO_CLIENT_ID"],
        "client_secret": os.environ["ZOHO_CLIENT_SECRET"],
        "grant_type": "refresh_token",
    }

    response = requests.post(url, params=params, timeout=10)
    data = response.json()

    if "access_token" not in data:
        raise RuntimeError(f"Token refresh failed: {data}")

    # Cache it
    _token_cache["access_token"] = data["access_token"]
    _token_cache["expires_at"] = time.time() + data.get("expires_in", 3600)

    return data["access_token"]
