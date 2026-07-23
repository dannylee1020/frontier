"""Small resilient HTTP helpers used by provider adapters."""

from __future__ import annotations

import json
import os
import time
from email.utils import parsedate_to_datetime
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class TransportError(RuntimeError):
    """An HTTP or response decoding failure."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


def _retry_delay(error: HTTPError | None, attempt: int) -> float:
    if error is not None:
        retry_after = error.headers.get("Retry-After")
        if retry_after:
            try:
                return min(float(retry_after), 30.0)
            except ValueError:
                try:
                    target = parsedate_to_datetime(retry_after).timestamp()
                    return max(0.0, min(target - time.time(), 30.0))
                except (TypeError, ValueError, OverflowError):
                    pass
    return min(0.5 * (2**attempt), 5.0)


def request_bytes(
    url: str,
    *,
    headers: dict[str, str] | None = None,
    timeout: float = 20.0,
    max_retries: int = 2,
) -> bytes:
    request_headers = {
        "Accept": "application/json, application/xml, text/xml, */*",
        "User-Agent": os.environ.get(
            "FRONTIER_USER_AGENT", "frontier-research-skill/0.1 (academic discovery)"
        ),
    }
    if headers:
        request_headers.update(headers)

    last_error: Exception | None = None
    for attempt in range(max_retries + 1):
        try:
            request = Request(url, headers=request_headers, method="GET")
            with urlopen(request, timeout=timeout) as response:
                return response.read()
        except HTTPError as error:
            last_error = error
            if error.code not in {408, 425, 429, 500, 502, 503, 504} or attempt >= max_retries:
                detail = error.read(300).decode("utf-8", errors="replace").strip()
                suffix = f": {detail}" if detail else ""
                raise TransportError(
                    f"HTTP {error.code} while fetching {url}{suffix}", error.code
                ) from error
            time.sleep(_retry_delay(error, attempt))
        except (URLError, TimeoutError, OSError) as error:
            last_error = error
            if attempt >= max_retries:
                raise TransportError(f"Network error while fetching {url}: {error}") from error
            time.sleep(_retry_delay(None, attempt))

    raise TransportError(f"Request failed for {url}: {last_error}") from last_error


def request_json_value(
    url: str,
    *,
    headers: dict[str, str] | None = None,
    timeout: float = 20.0,
    max_retries: int = 2,
) -> Any:
    payload = request_bytes(
        url, headers=headers, timeout=timeout, max_retries=max_retries
    )
    try:
        return json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise TransportError(f"Invalid JSON response from {url}") from error


def request_json(
    url: str,
    *,
    headers: dict[str, str] | None = None,
    timeout: float = 20.0,
    max_retries: int = 2,
) -> dict[str, Any]:
    decoded = request_json_value(
        url, headers=headers, timeout=timeout, max_retries=max_retries
    )
    if not isinstance(decoded, dict):
        raise TransportError(f"Expected a JSON object from {url}")
    return decoded


def request_text(
    url: str,
    *,
    headers: dict[str, str] | None = None,
    timeout: float = 20.0,
    max_retries: int = 2,
) -> str:
    payload = request_bytes(
        url,
        headers={"Accept": "application/atom+xml, application/xml, text/xml, */*", **(headers or {})},
        timeout=timeout,
        max_retries=max_retries,
    )
    return payload.decode("utf-8", errors="replace")
