import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from leetcode_client import LeetCodeClient
import sync


class LeetCodeClientTests(unittest.TestCase):
    def setUp(self):
        self.client = LeetCodeClient("example", "test-session")

    def test_null_submission_has_actionable_error(self):
        with patch.object(self.client, "_post", return_value={"submissionDetails": None}):
            with self.assertRaisesRegex(RuntimeError, "submission 123.*LEETCODE_SESSION"):
                self.client.submission_detail("123")

    def test_submission_details_are_preserved(self):
        detail = {"code": "print(1)", "timestamp": 123}
        with patch.object(self.client, "_post", return_value={"submissionDetails": detail}):
            self.assertIs(self.client.submission_detail("123"), detail)

    def test_http_failure_is_raised_before_json_is_read(self):
        response = Mock()
        response.raise_for_status.side_effect = requests.HTTPError("403 Forbidden")
        with patch.object(self.client.s, "post", return_value=response):
            with self.assertRaises(requests.HTTPError):
                self.client._post("query", {})
        response.json.assert_not_called()

    def test_null_submission_does_not_write_files_or_advance_checkpoint(self):
        with (
            patch.dict("os.environ", {"LEETCODE_USERNAME": "example", "LEETCODE_SESSION": "test-session"}),
            patch.object(sync, "OUT_DIR"),
            patch.object(sync, "load_state", return_value={"last_sync_epoch": 100}),
            patch.object(sync, "save_state") as save_state,
            patch.object(sync, "write_problem_files_if_changed") as write_files,
            patch.object(LeetCodeClient, "recent_accepted", return_value=[
                {"id": "123", "titleSlug": "two-sum", "timestamp": "200"}
            ]),
            patch.object(LeetCodeClient, "_post", return_value={"submissionDetails": None}),
        ):
            with self.assertRaisesRegex(RuntimeError, "submission 123"):
                sync.main(run_state={})
        save_state.assert_not_called()
        write_files.assert_not_called()


if __name__ == "__main__":
    unittest.main()
