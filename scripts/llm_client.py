from __future__ import annotations

import json
import os
import requests
from typing import Any, Dict


class LLMClient:
    def __init__(self):
        self.provider = (os.environ.get("LLM_PROVIDER") or "groq").strip().lower()
        self.model = (os.environ.get("LLM_MODEL") or "").strip()

        if self.provider == "groq":
            self.api_key = (os.environ.get("GROQ_API_KEY") or "").strip()
            self.base_url = "https://api.groq.com/openai/v1"
            if not self.model:
                self.model = "openai/gpt-oss-120b"
        elif self.provider == "openrouter":
            self.api_key = (os.environ.get("OPENROUTER_API_KEY") or "").strip()
            self.base_url = "https://openrouter.ai/api/v1"
            if not self.model:
                self.model = "mistralai/mistral-7b-instruct:free"
        else:
            raise ValueError(f"Unknown LLM_PROVIDER: {self.provider}")

    def enabled(self) -> bool:
        return bool(self.api_key and self.model)

    def chat_json(self, system: str, user: str, timeout: int = 60) -> Dict[str, Any]:
        if not self.enabled():
            raise RuntimeError("LLM not configured (missing API key or model).")

        url = f"{self.base_url}/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

        if self.provider == "openrouter":
            headers["HTTP-Referer"] = "https://github.com/"
            headers["X-Title"] = "leetcode-sync-bot"

        payload = {
            "model": self.model,
            "temperature": 0.2,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "response_format": {"type": "json_object"},
        }

        r = requests.post(url, headers=headers, json=payload, timeout=timeout)
        r.raise_for_status
        data = r.json()

        content = data["choices"][0]["message"]["content"]
        return json.loads(content)