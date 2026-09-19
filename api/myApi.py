"""
myApi.py
Only HTTP calls to the billing API. No MCP logic here.
"""
import os
from typing import Optional, Union

import httpx
from dotenv import load_dotenv

load_dotenv()

API_BASE = os.getenv("DEPOT_API_URL", "https://backendfacturation.onrender.com")
TIMEOUT = 90  # seconds (Render free tier can be slow to wake up)


def _assert_config() -> None:
    if not API_BASE:
        raise RuntimeError("Missing DEPOT_API_URL env var")


def _client() -> httpx.Client:
    return httpx.Client(timeout=TIMEOUT, http2=False, follow_redirects=True)


def api_get(path: str, params: Optional[dict] = None) -> Union[list, dict]:
    _assert_config()
    with _client() as client:
        res = client.get(f"{API_BASE}{path}", params=params,
                         headers={"Accept": "application/json"})
        res.raise_for_status()
        data = res.json()
        # The API may return a bare list or a {"value": [...]} object
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            return data.get("value", [])
        return data


def api_post(path: str, body: dict) -> Union[list, dict]:
    _assert_config()
    with _client() as client:
        res = client.post(f"{API_BASE}{path}", json=body,
                          headers={"Content-Type": "application/json",
                                   "Accept": "application/json"})
        res.raise_for_status()
        return res.json()


def api_put(path: str, body: dict) -> Union[list, dict]:
    _assert_config()
    with _client() as client:
        res = client.put(f"{API_BASE}{path}", json=body,
                         headers={"Content-Type": "application/json",
                                  "Accept": "application/json"})
        res.raise_for_status()
        return res.json()


def api_delete(path: str) -> Union[list, dict]:
    _assert_config()
    with _client() as client:
        res = client.delete(f"{API_BASE}{path}",
                            headers={"Accept": "application/json"})
        res.raise_for_status()
        return res.json()


def _extraire_erreur(err):
    reponse = getattr(err, "response", None)
    if reponse is not None:
        status = getattr(reponse, "status_code", "?")
        try:
            return f"HTTP {status}: {reponse.json()}"
        except ValueError:
            text = getattr(reponse, "text", "")
            if text:
                return f"HTTP {status}: {text}"
            return f"HTTP {status}: réponse vide, headers={dict(reponse.headers)}"
    return f"{type(err).__name__}: {str(err) or 'aucun message'}"