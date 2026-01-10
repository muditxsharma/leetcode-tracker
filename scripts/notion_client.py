from __future__ import annotations

import datetime as dt
import requests
from typing import Any, Dict, List, Optional

NOTION_API = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"


def _iso_now() -> str:
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


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

    def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        r = self.s.post(f"{NOTION_API}{path}", json=payload, timeout=30)
        r.raise_for_status()
        return r.json()

    def _patch(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        r = self.s.patch(f"{NOTION_API}{path}", json=payload, timeout=30)
        r.raise_for_status()
        return r.json()

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        r = self.s.get(f"{NOTION_API}{path}", params=params or {}, timeout=30)
        r.raise_for_status()
        return r.json()

    def _delete(self, path: str) -> Dict[str, Any]:
        r = self.s.delete(f"{NOTION_API}{path}", timeout=30)
        r.raise_for_status()
        return r.json() if r.text else {}

    def find_page(self, platform: str, slug: str) -> Optional[str]:
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
            params = {}
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

    def upsert_problem(self, meta: Dict[str, Any], readme_md: str, code: str, repo_path: str) -> str:
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
        solved_iso = dt.datetime.utcfromtimestamp(solved_ts).replace(microsecond=0).isoformat() + "Z"
        now_iso = _iso_now()

        page_id = self.find_page(platform=platform, slug=slug)

        props: Dict[str, Any] = {
            "Name": {"title": [{"text": {"content": title}}]},
            "Platform": {"select": {"name": platform}},
            "Slug": {"rich_text": [{"text": {"content": slug}}]},
            "URL": {"url": url},
            "Difficulty": {"select": {"name": difficulty}} if difficulty else {"select": None},
            "Tags": {"multi_select": [{"name": t} for t in tags]},
            "Language": {"select": {"name": lang}} if lang else {"select": None},
            "Runtime": {"rich_text": [{"text": {"content": runtime}}]} if runtime else {"rich_text": []},
            "Memory": {"rich_text": [{"text": {"content": memory}}]} if memory else {"rich_text": []},
            "SubmissionId": {"rich_text": [{"text": {"content": submission_id}}]} if submission_id else {"rich_text": []},
            "SolvedAt": {"date": {"start": solved_iso}} if solved_ts else {"date": None},
            "RepoPath": {"rich_text": [{"text": {"content": repo_path}}]} if repo_path else {"rich_text": []},
            "LastSyncedAt": {"date": {"start": now_iso}},
        }

        if page_id is None:
            created = self._post(
                "/pages",
                {"parent": {"database_id": self.database_id}, "properties": props},
            )
            page_id = created["id"]
        else:
            self._patch(f"/pages/{page_id}", {"properties": props})

        self._clear_children(page_id)

        blocks = [
            {
                "object": "block",
                "type": "callout",
                "callout": {
                    "rich_text": [
                        {"type": "text", "text": {"content": f"{platform} • {difficulty} • {lang}"}},
                        {"type": "text", "text": {"content": f"  |  Runtime: {runtime}  |  Memory: {memory}"}},
                    ],
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
            {
                "object": "block",
                "type": "code",
                "code": {"language": "markdown", "rich_text": [{"type": "text", "text": {"content": readme_md[:20000]}}]},
            },
            {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "Solution"}}]}},
            {
                "object": "block",
                "type": "code",
                "code": {
                    "language": "python" if lang.lower().startswith("python") else "plain text",
                    "rich_text": [{"type": "text", "text": {"content": (code or "")[:20000]}}],
                },
            },
        ]

        self._patch(f"/blocks/{page_id}/children", {"children": blocks})
        return page_id