"""Official X API v2 Recent Search adapter for social momentum."""

from __future__ import annotations

import json
import os
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

from ..models import SearchRequest, XPost, XSearchResponse
from ..normalize import clean_text
from ..transport import TransportError, request_json
from ..x_query import build_x_query, x_query_budget


_ENDPOINT = "https://api.x.com/2/tweets/search/recent"
_RECENT_DAYS = 7
_MIN_END_LAG = timedelta(seconds=30)


def _utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _format_time(value: datetime) -> str:
    return _utc(value).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_time(value: object) -> datetime | None:
    text = clean_text(value)
    if not text:
        return None
    try:
        return _utc(datetime.fromisoformat(text.replace("Z", "+00:00")))
    except ValueError:
        return None


def effective_window(
    request: SearchRequest,
    *,
    now: datetime | None = None,
) -> tuple[datetime, datetime] | None:
    """Return the request intersection with X Recent Search's recent window."""

    current = _utc(now or datetime.now(timezone.utc))
    recent_start = current - timedelta(days=min(request.x_days, _RECENT_DAYS))
    recent_end = current - _MIN_END_LAG
    requested_start = datetime.combine(request.since, time.min, tzinfo=timezone.utc)
    requested_end = datetime.combine(
        request.until + timedelta(days=1), time.min, tzinfo=timezone.utc
    )
    start = max(requested_start, recent_start)
    end = min(requested_end, recent_end)
    return (start, end) if start < end else None


def _error_text(errors: object) -> str | None:
    if not isinstance(errors, list):
        return clean_text(errors)
    messages: list[str] = []
    for item in errors:
        if not isinstance(item, dict):
            continue
        message = clean_text(item.get("detail") or item.get("message") or item.get("title"))
        if message and message not in messages:
            messages.append(message)
    return "; ".join(messages) if messages else None


class _AccountRegistry:
    """Optional annotations; these never restrict broad topic retrieval."""

    def __init__(self, payload: object):
        self.by_id: dict[str, tuple[str, str]] = {}
        self.by_username: dict[str, tuple[str, str]] = {}
        if not isinstance(payload, dict):
            return
        accounts = payload.get("accounts", [])
        if not isinstance(accounts, list):
            return
        for account in accounts:
            if not isinstance(account, dict):
                continue
            organization = clean_text(account.get("organization")) or "unknown"
            account_type = clean_text(account.get("account_type")) or "known"
            author_class = {
                "official_lab": "official",
                "paper_author": "paper_author",
                "practitioner": "practitioner",
                "commentator": "commentator",
            }.get(account_type, "known")
            usernames = account.get("usernames", [])
            if isinstance(usernames, str):
                usernames = [usernames]
            if isinstance(usernames, list):
                for username in usernames:
                    normalized = clean_text(username)
                    if normalized:
                        self.by_username[normalized.casefold().lstrip("@")] = (
                            author_class,
                            organization,
                        )
            author_id = clean_text(account.get("author_id") or account.get("user_id"))
            if author_id:
                self.by_id[author_id] = (author_class, organization)

    @classmethod
    def load(cls) -> "_AccountRegistry":
        path = Path(__file__).resolve().parents[3] / "references" / "x-sources.json"
        try:
            return cls(json.loads(path.read_text(encoding="utf-8")))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            return cls({})

    def classify(self, author_id: object, username: object) -> tuple[str, str]:
        author_key = clean_text(author_id)
        username_key = (clean_text(username) or "").casefold().lstrip("@")
        if author_key and author_key in self.by_id:
            return self.by_id[author_key]
        if username_key and username_key in self.by_username:
            return self.by_username[username_key]
        return "unknown", "unknown"


class XRecentAdapter:
    """Search broad topic branches through official X Recent Search."""

    name = "x_recent"
    role = "social_momentum"
    endpoint = _ENDPOINT
    max_concurrency = 1

    @staticmethod
    def is_configured() -> bool:
        return bool(os.environ.get("X_BEARER_TOKEN", "").strip())

    @staticmethod
    def _token() -> str:
        token = os.environ.get("X_BEARER_TOKEN", "").strip()
        if not token:
            raise RuntimeError("X_BEARER_TOKEN is required when X search is enabled")
        return token

    @staticmethod
    def _metrics(value: object) -> dict[str, int]:
        if not isinstance(value, dict):
            return {}
        result: dict[str, int] = {}
        for key in (
            "impression_count",
            "like_count",
            "retweet_count",
            "reply_count",
            "quote_count",
            "bookmark_count",
        ):
            raw = value.get(key)
            if isinstance(raw, int) and not isinstance(raw, bool):
                result[key] = raw
        return result

    @staticmethod
    def _linked_urls(value: object) -> list[str]:
        if not isinstance(value, dict):
            return []
        entities = value.get("entities")
        if not isinstance(entities, dict):
            return []
        urls = entities.get("urls")
        if not isinstance(urls, list):
            return []
        result: list[str] = []
        for item in urls:
            if not isinstance(item, dict):
                continue
            url = clean_text(item.get("expanded_url") or item.get("url"))
            if url and url not in result:
                result.append(url)
        return result

    @classmethod
    def parse_results(
        cls,
        payload: dict[str, Any],
        query: str,
        registry: _AccountRegistry | None = None,
        window: tuple[datetime, datetime] | None = None,
    ) -> list[XPost]:
        data = payload.get("data", [])
        if not isinstance(data, list):
            raise ValueError("X response did not contain a data list")
        registry = registry or _AccountRegistry({})
        users: dict[str, dict[str, Any]] = {}
        includes = payload.get("includes")
        if isinstance(includes, dict) and isinstance(includes.get("users"), list):
            for item in includes["users"]:
                if isinstance(item, dict) and clean_text(item.get("id")):
                    users[str(item["id"])] = item

        posts: list[XPost] = []
        for item in data:
            if not isinstance(item, dict):
                continue
            post_id = clean_text(item.get("id"))
            text = clean_text(item.get("text"))
            if not post_id or not text:
                continue
            created = _parse_time(item.get("created_at"))
            # A timestamp is required to honor the effective seven-day window;
            # silently retaining an undated post would weaken coverage claims.
            if created is None:
                continue
            if window and not (window[0] <= created < window[1]):
                continue
            author_id = clean_text(item.get("author_id"))
            user = users.get(author_id or "", {})
            username = clean_text(user.get("username"))
            author_name = clean_text(user.get("name"))
            author_class, organization = registry.classify(author_id, username)
            referenced: list[dict[str, str]] = []
            raw_references = item.get("referenced_tweets")
            if isinstance(raw_references, list):
                for reference in raw_references:
                    if not isinstance(reference, dict):
                        continue
                    reference_id = clean_text(reference.get("id"))
                    reference_type = clean_text(reference.get("type"))
                    if reference_id and reference_type:
                        referenced.append({"id": reference_id, "type": reference_type})
            edit_history = item.get("edit_history_tweet_ids")
            edit_ids = [
                clean_text(value) or ""
                for value in edit_history
                if clean_text(value)
            ] if isinstance(edit_history, list) else [post_id]
            url = (
                f"https://x.com/{username}/status/{post_id}"
                if username
                else f"https://x.com/i/web/status/{post_id}"
            )
            posts.append(
                XPost(
                    post_id=post_id,
                    text=text,
                    author_id=author_id,
                    username=username,
                    author_name=author_name,
                    organization=organization,
                    author_class=author_class,
                    created_at=_format_time(created),
                    url=url,
                    conversation_id=clean_text(item.get("conversation_id")),
                    referenced_posts=referenced,
                    linked_urls=cls._linked_urls(item),
                    public_metrics=cls._metrics(item.get("public_metrics")),
                    matched_queries=[query],
                    edit_history_ids=edit_ids,
                )
            )
        return posts

    def search(self, query: str, request: SearchRequest) -> XSearchResponse:
        token = self._token()
        compiled_query = build_x_query(query)
        window = effective_window(request)
        if window is None:
            return XSearchResponse(
                source=self.name,
                query=query,
                status="unavailable",
                api_query=compiled_query,
                error="requested date window does not overlap X Recent Search coverage",
            )

        budget = x_query_budget(request.queries, request.x_candidate_limit, query)
        if budget < 10:
            raise ValueError("X candidate limit must allocate at least 10 posts per query")
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }
        registry = _AccountRegistry.load()
        posts: list[XPost] = []
        seen_ids: set[str] = set()
        next_token: str | None = None
        page_error: str | None = None
        truncated = False

        while len(posts) < budget:
            params: dict[str, str | int] = {
                "query": compiled_query,
                "start_time": _format_time(window[0]),
                "end_time": _format_time(window[1]),
                "max_results": min(100, budget - len(posts)),
                "tweet.fields": (
                    "author_id,conversation_id,created_at,entities,lang,"
                    "public_metrics,referenced_tweets,edit_history_tweet_ids"
                ),
                "expansions": "author_id",
                "user.fields": "name,username",
            }
            if next_token:
                params["next_token"] = next_token
            url = f"{self.endpoint}?{urlencode(params)}"
            try:
                payload = request_json(
                    url,
                    headers=headers,
                    timeout=request.timeout_seconds,
                    max_retries=request.max_retries,
                )
            except TransportError as error:
                page_error = str(error)
                status = "rate-limited" if error.status_code == 429 else "error"
                return XSearchResponse(
                    source=self.name,
                    query=query,
                    status="partial" if posts else status,
                    posts=posts,
                    api_query=compiled_query,
                    effective_since=_format_time(window[0]),
                    effective_until=_format_time(window[1]),
                    error=page_error,
                    truncated=bool(posts),
                )

            response_error = _error_text(payload.get("errors"))
            page_posts = self.parse_results(payload, query, registry, window)
            for post in page_posts:
                if post.post_id not in seen_ids:
                    seen_ids.add(post.post_id)
                    posts.append(post)
                    if len(posts) >= budget:
                        break
            meta = payload.get("meta")
            next_token = (
                clean_text(meta.get("next_token"))
                if isinstance(meta, dict)
                else None
            )
            if response_error:
                page_error = response_error
                if posts:
                    break
                return XSearchResponse(
                    source=self.name,
                    query=query,
                    status="error",
                    api_query=compiled_query,
                    effective_since=_format_time(window[0]),
                    effective_until=_format_time(window[1]),
                    error=response_error,
                )
            if not next_token:
                break
            if len(posts) >= budget:
                truncated = True
                break

        return XSearchResponse(
            source=self.name,
            query=query,
            status="partial" if page_error else "ok",
            posts=posts,
            api_query=compiled_query,
            effective_since=_format_time(window[0]),
            effective_until=_format_time(window[1]),
            error=page_error,
            truncated=truncated,
        )
