from __future__ import annotations

LANG_TO_EXT = {
    "python": "py",
    "python3": "py",
    "python2": "py",
    "cpp": "cpp",
    "c++": "cpp",
    "java": "java",
    "javascript": "js",
    "typescript": "ts",
    "c": "c",
    "csharp": "cs",
    "c#": "cs",
    "golang": "go",
    "go": "go",
    "ruby": "rb",
    "swift": "swift",
    "kotlin": "kt",
    "rust": "rs",
    "php": "php",
    "scala": "scala",
}

def lang_to_ext(lang: str) -> str:
    if not lang:
        return "txt"
    key = lang.strip().lower()
    return LANG_TO_EXT.get(key, "txt")