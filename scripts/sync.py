from __future__ import annotations

from dotenv import load_dotenv
load_dotenv()

import json
import os
import re
import traceback
from pathlib import Path
from typing import Any, Dict, List, Tuple

from email_client import EmailClient
from leetcode_client import LeetCodeClient
from notion_client import NotionClient
from render_readme import build_readme
from lang_map import lang_to_ext
from score import runtime_ms, memory_mb

ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "state.json"
OUT_DIR = ROOT / "leetcode"


def slugify_folder(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9\-]+", "-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s or "problem"


def load_state() -> Dict[str, Any]:
    if not STATE_PATH.exists():
        return {"last_sync_epoch": 0}
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def save_state(state: Dict[str, Any]) -> None:
    STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")


def compute_problem_artifacts(meta: Dict[str, Any], code: str) -> Dict[str, str]:
    """
    Returns the exact content we want to write for this problem.
    """
    readme = build_readme(meta, code)
    meta_json = json.dumps(meta, indent=2)
    ext = lang_to_ext(meta.get("lang", ""))
    solution_name = f"solution.{ext}"

    return {
        "meta.json": meta_json,
        "README.md": readme,
        solution_name: code or "",
    }


def write_problem_files_if_changed(meta: Dict[str, Any], code: str) -> Tuple[Path, bool]:
    """
    Writes only if different.
    Returns (folder_path, changed_bool).
    """
    slug = meta["titleSlug"]
    folder = OUT_DIR / slugify_folder(slug)
    folder.mkdir(parents=True, exist_ok=True)

    artifacts = compute_problem_artifacts(meta, code)
    changed = False

    # If solution extension changed, remove old solution.* files
    desired_solution = next(k for k in artifacts.keys() if k.startswith("solution."))
    for p in folder.glob("solution.*"):
        if p.name != desired_solution:
            p.unlink()
            changed = True

    # Compare and write each file
    for name, content in artifacts.items():
        path = folder / name
        existing = path.read_text(encoding="utf-8") if path.exists() else None
        if existing != content:
            path.write_text(content, encoding="utf-8")
            changed = True

    return folder, changed


def choose_best(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Score by:
      1) lower runtime (ms) if parseable
      2) lower memory (MB) if parseable
      3) latest timestamp
    """
    def key_fn(item: Dict[str, Any]) -> Tuple[float, float, int]:
        meta = item["meta"]
        r = runtime_ms(meta.get("runtimeDisplay") or "")
        m = memory_mb(meta.get("memoryDisplay") or "")
        ts = int(meta.get("timestamp") or 0)

        r_key = r if r is not None else 1e18
        m_key = m if m is not None else 1e18
        return (r_key, m_key, -ts)

    return sorted(records, key=key_fn)[0]


def main(run_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Returns a summary dict used for email notification.
    """
    username = os.environ.get("LEETCODE_USERNAME", "").strip()
    leetcode_session = os.environ.get("LEETCODE_SESSION", "").strip()
    leetcode_csrf = os.environ.get("LEETCODE_CSRF", "").strip() or None

    notion_token = os.environ.get("NOTION_TOKEN", "").strip()
    notion_db = os.environ.get("NOTION_DATABASE_ID", "").strip()

    if not username:
        raise SystemExit("Missing LEETCODE_USERNAME env var.")
    if not leetcode_session:
        raise SystemExit("Missing LEETCODE_SESSION env var (cookie).")

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    state = load_state()
    last_sync = int(state.get("last_sync_epoch", 0))

    lc = LeetCodeClient(username=username, session_cookie=leetcode_session, csrf_token=leetcode_csrf)

    recent = lc.recent_accepted(limit=50)
    new_items = [x for x in recent if int(x.get("timestamp", "0")) > last_sync]

    if not new_items:
        print("No new accepted submissions since last sync.")
        return {
            "github_updated": False,
            "notion_updated": False,
            "slugs_checked": [],
            "slugs_updated": [],
            "max_ts": last_sync,
        }

    # Group by problem slug
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    max_ts = last_sync

    for item in new_items:
        submission_id = item["id"]
        title_slug = item["titleSlug"]

        sub = lc.submission_detail(submission_id)
        q = lc.question_detail(title_slug)

        ts = int(sub.get("timestamp") or item.get("timestamp") or 0)
        max_ts = max(max_ts, ts)

        lang_node = sub.get("lang") or {}
        lang_name = lang_node.get("name") or lang_node.get("verboseName") or ""

        meta: Dict[str, Any] = {
            "platform": "leetcode",
            "username": username,
            "submissionId": submission_id,
            "timestamp": ts,
            "title": q["title"],
            "titleSlug": q["titleSlug"],
            "questionId": q.get("questionId"),
            "difficulty": q.get("difficulty"),
            "tags": [t["name"] for t in (q.get("topicTags") or [])],
            "url": f"https://leetcode.com/problems/{q['titleSlug']}/",
            "lang": lang_name,
            "runtime": sub.get("runtime"),
            "runtimeDisplay": sub.get("runtimeDisplay"),
            "memory": sub.get("memory"),
            "memoryDisplay": sub.get("memoryDisplay"),
            "content": q.get("content"),  # HTML stored in meta.json
        }

        record = {"meta": meta, "code": sub.get("code", "")}
        grouped.setdefault(title_slug, []).append(record)

    # Optional Notion client
    notion = None
    if notion_token and notion_db:
        notion = NotionClient(token=notion_token, database_id=notion_db)
    else:
        print("Notion not configured (NOTION_TOKEN / NOTION_DATABASE_ID missing). Skipping Notion sync.")

    github_updated = False
    notion_updated = False
    slugs_checked: List[str] = []
    slugs_updated: List[str] = []

    for slug, records in grouped.items():
        best = choose_best(records)
        meta = best["meta"]
        code = best["code"]

        folder, changed = write_problem_files_if_changed(meta, code)
        repo_path = str(folder.relative_to(ROOT)).replace("\\", "/")

        slugs_checked.append(slug)

        if changed:
            github_updated = True
            slugs_updated.append(slug)
            print(f"Updated files: {slug} (submission {meta['submissionId']}, lang={meta.get('lang')})")
        else:
            print(f"No file changes: {slug} (best submission {meta['submissionId']})")

        if notion and changed:
            readme_md = (folder / "README.md").read_text(encoding="utf-8")
            notion.upsert_problem(meta=meta, readme_md=readme_md, code=code, repo_path=repo_path)
            notion_updated = True
            print(f"Notion upserted: {slug}")
        elif notion and not changed:
            print(f"Skipped Notion (no changes): {slug}")

    state["last_sync_epoch"] = max_ts
    save_state(state)
    print(f"Updated state.last_sync_epoch = {max_ts}")

    return {
        "github_updated": github_updated,
        "notion_updated": notion_updated,
        "slugs_checked": slugs_checked,
        "slugs_updated": slugs_updated,
        "max_ts": max_ts,
    }


if __name__ == "__main__":
    email = EmailClient()

    status = "SUCCESS"
    summary: Dict[str, Any] = {
        "github_updated": False,
        "notion_updated": False,
        "slugs_checked": [],
        "slugs_updated": [],
        "max_ts": 0,
    }
    errors: List[str] = []

    try:
        summary = main(run_state={})
    except Exception:
        status = "FAILED"
        errors.append(traceback.format_exc())
        raise
    finally:
        if email.enabled():
            from datetime import datetime, timezone

            ts = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

            subject = f"[LeetCode Sync] {status}"
            body_lines = [
                f"LeetCode Sync Job Status: {status}",
                "",
                f"GitHub Updated: {summary.get('github_updated', False)}",
                f"Notion Updated: {summary.get('notion_updated', False)}",
                "",
                "Problems Checked:",
                "\n".join(summary.get("slugs_checked", []) or []) or "None",
                "",
                "Problems Updated:",
                "\n".join(summary.get("slugs_updated", []) or []) or "None",
                "",
                "Errors:",
                "\n".join(errors) if errors else "None",
                "",
                f"Timestamp (UTC): {ts}",
            ]
            email.send(subject=subject, body="\n".join(body_lines))