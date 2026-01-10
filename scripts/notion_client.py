from __future__ import annotations

import datetime as dt
import requests
from typing import Any, Dict, List, Optional

NOTION_API = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"


def _iso_now() -> str:
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _chunk_text(s: str, max_len: int = 2000) -> List[Dict[str, Any]]:
    """
    Split text into Notion rich_text chunks (each <= max_len).
    Notion enforces a 2000 char limit per rich_text item.
    """
    s = s or ""
    chunks = [s[i : i + max_len] for i in range(0, len(s), max_len)]
    return [{"type": "text", "text": {"content": c}} for c in chunks if c] or [
        {"type": "text", "text": {"content": ""}}
    ]


class NotionClient:
    def __init__(self, token: str, database_id: str):
        self.token = token
        self.database_id = database_id
        self.s = requests.Session()
        self.s.headers.update(
            {
                "Authorization": f"Bearer {self.token}",
                "Notion-Version": NOTION_VERSION,
                "Content-Type": "application/json",
            }
        )

    def _request_json(
        self,
        method: str,
        path: str,
        payload: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        url = f"{NOTION_API}{path}"
        r = self.s.request(method, url, json=payload, params=params, timeout=30)

        try:
            data = r.json()
        except Exception:
            raise RuntimeError(
                f"Notion API returned non-JSON. method={method} status={r.status_code} body={r.text[:2000]}"
            )

        if not r.ok:
            raise RuntimeError(
                f"Notion API error. method={method} status={r.status_code} response={data}"
            )

        if isinstance(data, dict) and data.get("object") == "error":
            raise RuntimeError(f"Notion API error object: {data}")

        return data

    def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._request_json("POST", path, payload=payload)

    def _patch(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._request_json("PATCH", path, payload=payload)

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self._request_json("GET", path, params=params)

    def _delete(self, path: str) -> Dict[str, Any]:
        return self._request_json("DELETE", path)

    def find_page(self, platform: str, slug: str) -> Optional[str]:
        """
        DB needs properties:
          - Platform (select)
          - Slug (rich_text)
        """
        payload = {
            "filter": {
                "and": [
                    {"property": "Platform", "select": {"equals": platform}},
                    {"property": "Slug", "rich_text": {"equals": slug}},
                ]
            },
            "page_size": 1,
        }
        data = self._post(f"/databases/{self.database_id}/query", payload)
        results = data.get("results", [])
        if not results:
            return None
        return results[0]["id"]

    def _list_children(self, block_id: str) -> List[Dict[str, Any]]:
        children: List[Dict[str, Any]] = []
        cursor = None
        while True:
            params = {"page_size": 100}
            if cursor:
                params["start_cursor"] = cursor
            data = self._get(f"/blocks/{block_id}/children", params=params)
            children.extend(data.get("results", []))
            if not data.get("has_more"):
                break
            cursor = data.get("next_cursor")
        return children

    def _clear_children(self, page_id: str) -> None:
        blocks = self._list_children(page_id)
        for b in blocks:
            self._delete(f"/blocks/{b['id']}")

    def upsert_problem(
        self,
        meta: Dict[str, Any],
        readme_md: str,
        code: str,
        repo_path: str,
    ) -> str:
        """
        Aligned to YOUR DB schema (from your query output):
          - Name (title)
          - Platform (select)
          - Slug (rich_text)
          - URL (url)
          - Difficulty (select)
          - Tags (multi_select)
          - Language (select)
          - Performance metadata (rich_text)  <-- stores runtime+memory
          - Memory (rich_text)
          - SubmissionId (rich_text)
          - Dates (date)                     <-- used for solved timestamp
          - Repo integration (rich_text)     <-- used for repo path
          - LastSyncedAt (date)
        """
        platform = "LeetCode"

        slug = meta["titleSlug"]
        title = meta["title"]
        tags = meta.get("tags", []) or []
        difficulty = meta.get("difficulty") or ""
        lang = meta.get("lang") or ""
        runtime = meta.get("runtimeDisplay") or (str(meta.get("runtime")) if meta.get("runtime") else "")
        memory = meta.get("memoryDisplay") or (str(meta.get("memory")) if meta.get("memory") else "")
        submission_id = str(meta.get("submissionId") or "")
        url = meta.get("url") or ""
        solved_ts = int(meta.get("timestamp") or 0)
        solved_iso = (
            dt.datetime.utcfromtimestamp(solved_ts).replace(microsecond=0).isoformat() + "Z"
            if solved_ts
            else ""
        )
        now_iso = _iso_now()

        perf_parts = []
        if runtime:
            perf_parts.append(f"Runtime: {runtime}")
        if memory:
            perf_parts.append(f"Memory: {memory}")
        perf_text = " | ".join(perf_parts)

        page_id = self.find_page(platform=platform, slug=slug)

        props: Dict[str, Any] = {
            "Name": {"title": [{"text": {"content": title}}]},
            "Platform": {"select": {"name": platform}},
            "Slug": {"rich_text": [{"text": {"content": slug}}]},
            "URL": {"url": url},
            "Difficulty": {"select": {"name": difficulty}} if difficulty else {"select": None},
            "Tags": {"multi_select": [{"name": t} for t in tags]},
            "Language": {"select": {"name": lang}} if lang else {"select": None},
            "Performance metadata": {"rich_text": [{"text": {"content": perf_text}}]} if perf_text else {"rich_text": []},
            "Memory": {"rich_text": [{"text": {"content": memory}}]} if memory else {"rich_text": []},
            "SubmissionId": {"rich_text": [{"text": {"content": submission_id}}]} if submission_id else {"rich_text": []},
            "Dates": {"date": {"start": solved_iso}} if solved_iso else {"date": None},
            "Repo integration": {"rich_text": [{"text": {"content": repo_path}}]} if repo_path else {"rich_text": []},
            "LastSyncedAt": {"date": {"start": now_iso}},
        }

        if page_id is None:
            created = self._post(
                "/pages",
                {"parent": {"database_id": self.database_id}, "properties": props},
            )
            page_id = created.get("id")
            if not page_id:
                raise RuntimeError(f"Notion create page returned no 'id'. Response: {created}")
        else:
            self._patch(f"/pages/{page_id}", {"properties": props})

        # Replace page body
        self._clear_children(page_id)

        # Truncate total size (still chunk per 2000 chars)
        readme_short = (readme_md or "")[:20000]
        code_short = (code or "")[:20000]

        readme_rich = _chunk_text(readme_short, max_len=2000)
        code_rich = _chunk_text(code_short, max_len=2000)

        blocks = [
            {
                "object": "block",
                "type": "callout",
                "callout": {
                    "rich_text": _chunk_text(f"{platform} • {difficulty} • {lang}  |  {perf_text}", max_len=2000),
                    "icon": {"emoji": "🧩"},
                },
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {"type": "text", "text": {"content": "Problem link: "}},
                        {"type": "text", "text": {"content": url, "link": {"url": url}}},
                    ]
                },
            },
            {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "README"}}]}},
            {"object": "block", "type": "code", "code": {"language": "markdown", "rich_text": readme_rich}},
            {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "Solution"}}]}},
            {
                "object": "block",
                "type": "code",
                "code": {
                    "language": "python" if lang.lower().startswith("python") else "plain text",
                    "rich_text": code_rich,
                },
            },
        ]

        self._patch(f"/blocks/{page_id}/children", {"children": blocks})
        return page_id