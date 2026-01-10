from __future__ import annotations

import re
from html import unescape
from typing import Dict, Any, List

from llm_client import LLMClient


def _html_to_text(html: str) -> str:
    if not html:
        return ""
    s = unescape(html)
    s = re.sub(r"</(p|div|br|li|h1|h2|h3|h4|h5|h6)>", "\n", s, flags=re.I)
    s = re.sub(r"<br\s*/?>", "\n", s, flags=re.I)
    s = re.sub(r"<li>", "- ", s, flags=re.I)
    s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"\n{3,}", "\n\n", s).strip()
    return s


def _truncate(s: str, max_chars: int) -> str:
    if not s:
        return ""
    s = s.strip()
    return s if len(s) <= max_chars else s[:max_chars].rstrip() + "\n\n(Truncated.)"


def _fallback_readme(meta: Dict[str, Any], problem_text: str) -> str:
    title = meta["title"]
    url = meta["url"]
    difficulty = meta.get("difficulty", "")
    tags = meta.get("tags", [])
    lang = meta.get("lang", "")
    runtime = meta.get("runtimeDisplay") or meta.get("runtime") or ""
    memory = meta.get("memoryDisplay") or meta.get("memory") or ""
    tags_line = ", ".join(tags) if tags else ""

    snippet = _truncate(problem_text, 1200)

    return f"""# {title}

- **Platform:** LeetCode
- **Difficulty:** {difficulty}
- **Tags:** {tags_line}
- **Link:** {url}
- **Language (detected):** {lang}
- **Runtime:** {runtime}
- **Memory:** {memory}

## Problem (summary)

{snippet}

## Approach

_TBD_

## Complexity

- **Time:** _TBD_
- **Space:** _TBD_

## Pros

- _TBD_

## Cons

- _TBD_
"""


def build_readme(meta: Dict[str, Any], code: str) -> str:
    problem_text = _html_to_text(meta.get("content", ""))

    prompt_problem = _truncate(problem_text, 6000)
    prompt_code = _truncate(code or "", 9000)

    llm = LLMClient()
    if not llm.enabled():
        return _fallback_readme(meta, problem_text)

    system = (
        "You are a competitive programming coach. "
        "Given a LeetCode problem and a user's accepted solution code, "
        "write a high-quality README section: approach, complexity, pros/cons, edge cases. "
        "Be precise and do not invent constraints."
    )

    user = f"""
Return ONLY valid JSON with keys:
- approach_md (string markdown)
- time_complexity (string)
- space_complexity (string)
- pros (array of strings)
- cons (array of strings)
- edge_cases (array of strings)

Problem Title: {meta.get("title")}
Difficulty: {meta.get("difficulty")}
Tags: {", ".join(meta.get("tags", []) or [])}
URL: {meta.get("url")}

Problem (text):
{prompt_problem}

Solution code (detected lang: {meta.get("lang")}):
{prompt_code}
""".strip()

    try:
        out = llm.chat_json(system=system, user=user)
    except Exception:
        return _fallback_readme(meta, problem_text)

    title = meta["title"]
    url = meta["url"]
    difficulty = meta.get("difficulty", "")
    tags = meta.get("tags", [])
    lang = meta.get("lang", "")
    runtime = meta.get("runtimeDisplay") or meta.get("runtime") or ""
    memory = meta.get("memoryDisplay") or meta.get("memory") or ""
    tags_line = ", ".join(tags) if tags else ""

    approach_md = (out.get("approach_md") or "").strip()
    time_c = (out.get("time_complexity") or "TBD").strip()
    space_c = (out.get("space_complexity") or "TBD").strip()
    pros = out.get("pros") or []
    cons = out.get("cons") or []
    edge = out.get("edge_cases") or []

    def bullet(items: List[str]) -> str:
        items = [str(x).strip() for x in items if str(x).strip()]
        return "\n".join([f"- {x}" for x in items]) if items else "- _None_"

    problem_summary = _truncate(problem_text, 1200)

    return f"""# {title}

- **Platform:** LeetCode
- **Difficulty:** {difficulty}
- **Tags:** {tags_line}
- **Link:** {url}
- **Language (detected):** {lang}
- **Runtime:** {runtime}
- **Memory:** {memory}

## Problem (summary)

{problem_summary}

## Approach

{approach_md if approach_md else "_TBD_"}

## Complexity

- **Time:** {time_c}
- **Space:** {space_c}

## Pros

{bullet(pros)}

## Cons

{bullet(cons)}

## Edge cases

{bullet(edge)}
"""