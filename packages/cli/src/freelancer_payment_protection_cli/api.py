"""
Thin HTTP client for the freelancer-payment-protection FastAPI backend.

Every route this module calls is a real endpoint read directly from
apps/api/app/routers/*.py in the target repo:
  - clients.py:       GET/POST /api/v1/clients, GET/PUT/DELETE /api/v1/clients/{id}
  - invoices.py:       GET/POST /api/v1/invoices, GET /api/v1/invoices/{id},
                        PATCH /api/v1/invoices/{id}/status
  - escalations.py:    GET /api/v1/escalations, POST /api/v1/escalations/{id}/draft,
                        GET /api/v1/escalations/{id}/history
  - risk_scoring.py:    POST /api/v1/risk/score
"""
from __future__ import annotations

from typing import Any

import httpx

from . import auth, config


class ApiError(RuntimeError):
    def __init__(self, status_code: int, detail: str):
        super().__init__(f"{status_code}: {detail}")
        self.status_code = status_code
        self.detail = detail


class ApiClient:
    def __init__(self, base_url: str | None = None, http: httpx.Client | None = None):
        self.base_url = (base_url or config.api_url()).rstrip("/")
        self._http = http or httpx.Client(timeout=30.0)
        self._owns_http = http is None

    def close(self) -> None:
        if self._owns_http:
            self._http.close()

    def __enter__(self) -> "ApiClient":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()

    def _request(self, method: str, path: str, retried: bool = False, **kwargs: Any) -> httpx.Response:
        token = auth.get_valid_access_token(client=self._http)
        headers = kwargs.pop("headers", {}) or {}
        headers["Authorization"] = f"Bearer {token}"
        url = f"{self.base_url}{path}"
        response = self._http.request(method, url, headers=headers, **kwargs)

        if response.status_code == 401 and not retried:
            # Access token was rejected server-side (e.g. expired sooner than
            # our local clock expected). Force a refresh and retry once.
            creds = auth.load_credentials()
            if creds is not None:
                refreshed = auth.refresh(creds.refresh_token, client=self._http)
                auth.save_credentials(refreshed)
                return self._request(method, path, retried=True, **kwargs)

        if response.status_code >= 400:
            raise ApiError(response.status_code, _error_detail(response))

        return response

    def get(self, path: str, params: dict | None = None) -> Any:
        return self._request("GET", path, params=params).json()

    def post(self, path: str, json_body: dict | None = None) -> Any:
        return self._request("POST", path, json=json_body).json()

    def patch(self, path: str, json_body: dict | None = None) -> Any:
        return self._request("PATCH", path, json=json_body).json()

    def put(self, path: str, json_body: dict | None = None) -> Any:
        return self._request("PUT", path, json=json_body).json()

    def delete(self, path: str) -> None:
        self._request("DELETE", path)


def _error_detail(response: httpx.Response) -> str:
    try:
        data = response.json()
        if isinstance(data, dict) and "detail" in data:
            return str(data["detail"])
        return str(data)
    except ValueError:
        return response.text
