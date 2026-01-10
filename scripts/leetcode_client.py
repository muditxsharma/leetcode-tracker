from __future__ import annotations

import os
import time
import requests
from typing import Any, Dict, List, Optional

LEETCODE_GRAPHQL = "https://leetcode.com/graphql"

class LeetCodeClient:
    def __init__(self, username: str, session_cookie: str, csrf_token: Optional[str] = None):
        self.username = username
        self.s = requests.Session()

        # Cookies (auth for submission code/details)
        if session_cookie:
            self.s.cookies.set("LEETCODE_SESSION", session_cookie, domain=".leetcode.com")
        if csrf_token:
            self.s.cookies.set("csrftoken", csrf_token, domain=".leetcode.com")

        self.csrf_token = csrf_token

    def _post(self, query: str, variables: Dict[str, Any]) -> Dict[str, Any]:
        headers = {
            "Content-Type": "application/json",
            "Referer": "https://leetcode.com",
            "User-Agent": "leetcode-sync-bot/1.0",
        }
        # LeetCode sometimes expects x-csrftoken for authenticated queries
        if self.csrf_token:
            headers["x-csrftoken"] = self.csrf_token

        resp = self.s.post(
            LEETCODE_GRAPHQL,
            json={"query": query, "variables": variables},
            headers=headers,
            timeout=30,
        )
        resp.raise_for_status
        data = resp.json()
        if "errors" in data:
            raise RuntimeError(f"GraphQL errors: {data['errors']}")
        return data["data"]

    def recent_accepted(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Returns a list of recent accepted submissions for the user.
        Each item includes: id, title, titleSlug, timestamp
        """
        q = """
        query recentAcSubmissionList($username: String!, $limit: Int!) {
          recentAcSubmissionList(username: $username, limit: $limit) {
            id
            title
            titleSlug
            timestamp
          }
        }
        """
        data = self._post(q, {"username": self.username, "limit": limit})
        return data.get("recentAcSubmissionList") or []

    def submission_detail(self, submission_id: str) -> Dict[str, Any]:
        """
        Returns details including code and lang.
        """
        q = """
        query submissionDetails($submissionId: Int!) {
          submissionDetails(submissionId: $submissionId) {
            runtime
            runtimeDisplay
            memory
            memoryDisplay
            code
            lang {
              name
              verboseName
            }
            timestamp
            question {
              titleSlug
            }
          }
        }
        """
        data = self._post(q, {"submissionId": int(submission_id)})
        return data["submissionDetails"]

    def question_detail(self, title_slug: str) -> Dict[str, Any]:
        q = """
        query questionData($titleSlug: String!) {
          question(titleSlug: $titleSlug) {
            questionId
            title
            titleSlug
            content
            difficulty
            topicTags {
              name
              slug
            }
          }
        }
        """
        data = self._post(q, {"titleSlug": title_slug})
        return data["question"]