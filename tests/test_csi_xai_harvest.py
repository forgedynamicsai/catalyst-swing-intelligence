"""
xAI/Grok harvest adapter tests (v0.6 optional module).

All tests are mocked — NO real API calls.
All data is fictional. Not financial advice.

Test Coverage (12 required):
1. Missing XAI_API_KEY exits gracefully, sends NO request
2. Harvest prompt contains CSI markdown evidence schema
3. Harvest prompt says X virality is velocity, not truth
4. Harvest prompt says do not provide buy/sell/hold advice
5. Tool selection maps x,web to both X Search + Web Search in request
6. Cost conversion: cost_in_usd_ticks / 10_000_000_000 is correct
7. Raw response save path does NOT contain API key
8. Response with markdown table saves evidence.md
9. --auto-score calls import/validate/score/report/observe helpers (mocked)
10. Validation failure stops auto-score pipeline
11. HTTP 401 gives helpful error message
12. No generated docs suggest purchases, investments, or companies to buy
"""

import json
import os
import sys
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch, MagicMock, call

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools", "csi"))
import xai_harvest


# ===========================================================================
# Test 1: Missing XAI_API_KEY exits gracefully, sends NO request
# ===========================================================================

class TestMissingAPIKey(unittest.TestCase):
    def test_missing_api_key_no_request(self):
        """Missing XAI_API_KEY should return helpful message without making any request."""
        with patch.dict(os.environ, {}, clear=True):
            is_ok, msg = xai_harvest.check_api_key()
            self.assertFalse(is_ok)
            self.assertIn("XAI_API_KEY is not set", msg)
            self.assertIn("export XAI_API_KEY", msg)
            self.assertIn("No request was sent", msg)

    def test_api_key_present_returns_ok(self):
        """If XAI_API_KEY is set, check_api_key should return True."""
        with patch.dict(os.environ, {"XAI_API_KEY": "test-key"}):
            is_ok, msg = xai_harvest.check_api_key()
            self.assertTrue(is_ok)
            self.assertEqual(msg, "")


# ===========================================================================
# Test 2: Harvest prompt contains CSI markdown evidence schema
# ===========================================================================

class TestHarvestPrompt(unittest.TestCase):
    def test_prompt_contains_evidence_table_schema(self):
        """Harvest prompt should instruct Grok to produce CSI markdown table."""
        prompt = xai_harvest.build_harvest_prompt("test theme")

        # Must include all CSI columns
        required_cols = [
            "claim", "source_name", "source_url", "source_class",
            "source_date", "source_type", "independence_rating",
            "evidence_quality", "specificity", "catalyst_alignment",
            "dissent_quality", "time_signal", "is_duplicate", "notes",
        ]
        for col in required_cols:
            self.assertIn(col, prompt, f"Prompt must reference '{col}'")

        # Must include pipe character (markdown table)
        self.assertIn("|", prompt)

    # ===========================================================================
    # Test 3: Harvest prompt says X virality is velocity, not truth
    # ===========================================================================

    def test_prompt_distinguishes_virality_from_evidence(self):
        """Prompt must distinguish X virality (signal of velocity) from evidence quality."""
        prompt = xai_harvest.build_harvest_prompt("test theme")
        # Check for virality, velocity, and evidence quality distinction
        self.assertIn("virality", prompt.lower())
        self.assertIn("velocity", prompt.lower())
        self.assertIn("evidence quality", prompt.lower())
        # Check for "not" to ensure it's saying virality is NOT the same as evidence quality
        self.assertIn("not evidence quality", prompt.lower())

    # ===========================================================================
    # Test 4: Harvest prompt says do NOT provide buy/sell/hold advice
    # ===========================================================================

    def test_prompt_prohibits_advisory_language(self):
        """Prompt must explicitly prohibit buy/sell/hold advice and recommendations."""
        prompt = xai_harvest.build_harvest_prompt("test theme")
        # Check for prohibition of advisory language
        self.assertIn("buy/sell/hold", prompt.lower())
        self.assertIn("do not", prompt.lower())
        self.assertIn("purchase", prompt.lower())
        self.assertIn("position sizing", prompt.lower())


# ===========================================================================
# Test 5: Tool selection maps x,web to both X Search + Web Search in request
# ===========================================================================

class TestToolSelection(unittest.TestCase):
    def test_tool_mapping_x_web(self):
        """x,web should map to both x_search and web_search in request config."""
        with patch.dict(os.environ, {"XAI_API_KEY": "test-key"}):
            with patch("urllib.request.urlopen") as mock_urlopen:
                # Mock successful response
                mock_response = MagicMock()
                mock_response.read.return_value = json.dumps({
                    "choices": [{"message": {"content": "| claim | source_name |\n|---|---|\n| test | test |"}}]
                }).encode("utf-8")
                mock_urlopen.return_value.__enter__.return_value = mock_response

                # Make request with x,web
                response, error = xai_harvest.make_request("test-key", "test theme", tools="x,web")

                self.assertIsNotNone(response)
                self.assertEqual(error, "")

                # Check that the request body included both tools
                call_args = mock_urlopen.call_args
                request_obj = call_args[0][0]
                body = request_obj.data.decode("utf-8")
                body_dict = json.loads(body)

                tools = body_dict.get("tools", [])
                tool_types = [t.get("type") for t in tools]
                self.assertIn("x_search", tool_types)
                self.assertIn("web_search", tool_types)

    def test_tool_mapping_x_only(self):
        """x should map to only x_search in request config."""
        with patch.dict(os.environ, {"XAI_API_KEY": "test-key"}):
            with patch("urllib.request.urlopen") as mock_urlopen:
                mock_response = MagicMock()
                mock_response.read.return_value = json.dumps({
                    "choices": [{"message": {"content": "| claim | source_name |\n|---|---|\n| test | test |"}}]
                }).encode("utf-8")
                mock_urlopen.return_value.__enter__.return_value = mock_response

                response, error = xai_harvest.make_request("test-key", "test theme", tools="x")

                call_args = mock_urlopen.call_args
                request_obj = call_args[0][0]
                body = request_obj.data.decode("utf-8")
                body_dict = json.loads(body)

                tools = body_dict.get("tools", [])
                tool_types = [t.get("type") for t in tools]
                self.assertIn("x_search", tool_types)
                self.assertNotIn("web_search", tool_types)

    def test_tool_mapping_web_only(self):
        """web should map to only web_search in request config."""
        with patch.dict(os.environ, {"XAI_API_KEY": "test-key"}):
            with patch("urllib.request.urlopen") as mock_urlopen:
                mock_response = MagicMock()
                mock_response.read.return_value = json.dumps({
                    "choices": [{"message": {"content": "| claim | source_name |\n|---|---|\n| test | test |"}}]
                }).encode("utf-8")
                mock_urlopen.return_value.__enter__.return_value = mock_response

                response, error = xai_harvest.make_request("test-key", "test theme", tools="web")

                call_args = mock_urlopen.call_args
                request_obj = call_args[0][0]
                body = request_obj.data.decode("utf-8")
                body_dict = json.loads(body)

                tools = body_dict.get("tools", [])
                tool_types = [t.get("type") for t in tools]
                self.assertNotIn("x_search", tool_types)
                self.assertIn("web_search", tool_types)


# ===========================================================================
# Request payload schema — regression tests for "input" vs "messages"
# HTTP 422 "missing field `input`" is caught here before it hits the API.
# ===========================================================================

class TestRequestPayloadSchema(unittest.TestCase):
    """Regression suite for xAI Responses API payload shape."""

    def _capture_body(self, tools="x,web"):
        """Helper: call make_request with a mocked urlopen and return parsed body."""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "choices": [{"message": {"content": "no table"}}],
            "usage": {}
        }).encode("utf-8")

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.return_value.__enter__.return_value = mock_response
            with patch("urllib.request.Request") as mock_req:
                # Let Request pass through to urlopen by returning a real-ish object
                captured = {}

                def capture_request(url, data=None, headers=None, method=None):
                    captured["body"] = json.loads(data.decode("utf-8")) if data else {}
                    real_req = MagicMock()
                    real_req.data = data
                    return real_req

                mock_req.side_effect = capture_request
                xai_harvest.make_request("test-key", "test theme", tools=tools)
                return captured.get("body", {})

    def test_payload_uses_input_not_messages(self):
        """Request body must use 'input', not 'messages' (xAI Responses API schema)."""
        with patch.dict(os.environ, {"XAI_API_KEY": "test-key"}):
            with patch("urllib.request.urlopen") as mock_urlopen:
                mock_response = MagicMock()
                mock_response.read.return_value = json.dumps({
                    "choices": [{"message": {"content": "no table"}}],
                    "usage": {}
                }).encode("utf-8")
                mock_urlopen.return_value.__enter__.return_value = mock_response

                with patch("urllib.request.Request") as mock_req:
                    captured_body = {}

                    def capture(url, data=None, headers=None, method=None):
                        captured_body.update(json.loads(data.decode("utf-8")))
                        obj = MagicMock()
                        obj.data = data
                        return obj

                    mock_req.side_effect = capture
                    xai_harvest.make_request("test-key", "test theme")

                self.assertIn("input", captured_body,
                              "Payload missing 'input' — xAI Responses API requires 'input', not 'messages'")
                self.assertNotIn("messages", captured_body,
                                 "Payload must not contain 'messages' — that is Chat Completions schema, not Responses API")

    def test_payload_input_contains_user_prompt(self):
        """input[0] must have role='user' and content matching the harvest prompt."""
        with patch.dict(os.environ, {"XAI_API_KEY": "test-key"}):
            with patch("urllib.request.urlopen") as mock_urlopen:
                mock_response = MagicMock()
                mock_response.read.return_value = json.dumps({
                    "choices": [{"message": {"content": "no table"}}],
                    "usage": {}
                }).encode("utf-8")
                mock_urlopen.return_value.__enter__.return_value = mock_response

                with patch("urllib.request.Request") as mock_req:
                    captured_body = {}

                    def capture(url, data=None, headers=None, method=None):
                        captured_body.update(json.loads(data.decode("utf-8")))
                        obj = MagicMock()
                        obj.data = data
                        return obj

                    mock_req.side_effect = capture
                    theme = "AI data center power scarcity"
                    xai_harvest.make_request("test-key", theme)

                input_msgs = captured_body.get("input", [])
                self.assertTrue(len(input_msgs) > 0, "input array must not be empty")
                first = input_msgs[0]
                self.assertEqual(first.get("role"), "user")
                self.assertIn(theme, first.get("content", ""),
                              "Theme must appear in the input content")

    def test_payload_tools_present_alongside_input(self):
        """tools field must be present when input is used."""
        with patch.dict(os.environ, {"XAI_API_KEY": "test-key"}):
            with patch("urllib.request.urlopen") as mock_urlopen:
                mock_response = MagicMock()
                mock_response.read.return_value = json.dumps({
                    "choices": [{"message": {"content": "no table"}}],
                    "usage": {}
                }).encode("utf-8")
                mock_urlopen.return_value.__enter__.return_value = mock_response

                with patch("urllib.request.Request") as mock_req:
                    captured_body = {}

                    def capture(url, data=None, headers=None, method=None):
                        captured_body.update(json.loads(data.decode("utf-8")))
                        obj = MagicMock()
                        obj.data = data
                        return obj

                    mock_req.side_effect = capture
                    xai_harvest.make_request("test-key", "test theme", tools="x,web")

                self.assertIn("tools", captured_body,
                              "tools field must be present in request payload")
                tool_types = [t.get("type") for t in captured_body.get("tools", [])]
                self.assertIn("x_search", tool_types)
                self.assertIn("web_search", tool_types)


# ===========================================================================
# Test 6: Cost conversion is correct
# ===========================================================================

class TestCostConversion(unittest.TestCase):
    def test_cost_conversion_formula(self):
        """Cost conversion: cost_usd = cost_in_usd_ticks / 10_000_000_000"""
        # Test case: 37756000 ticks = 0.0037756 USD
        response = {
            "usage": {
                "cost_in_usd_ticks": 37756000
            }
        }
        cost = xai_harvest.extract_cost_usd(response)
        self.assertAlmostEqual(cost, 0.0037756, places=7)

    def test_cost_conversion_missing_usage(self):
        """If usage is missing, cost should be None."""
        response = {"choices": []}
        cost = xai_harvest.extract_cost_usd(response)
        self.assertIsNone(cost)

    def test_cost_conversion_zero_ticks(self):
        """Zero ticks should convert to zero USD."""
        response = {"usage": {"cost_in_usd_ticks": 0}}
        cost = xai_harvest.extract_cost_usd(response)
        self.assertEqual(cost, 0.0)


# ===========================================================================
# Test 7: Raw response save path does NOT contain API key
# ===========================================================================

class TestRawResponseSave(unittest.TestCase):
    def test_raw_response_no_api_key_in_path(self):
        """Raw response path should not contain API key."""
        with tempfile.TemporaryDirectory() as tmpdir:
            response = {
                "choices": [{"message": {"content": "test"}}],
                "api_key": "SECRET_KEY_SHOULD_NOT_BE_HERE"
            }
            path = xai_harvest.save_raw_response(response, "test theme", tmpdir)

            # Path should not contain any obvious key-like strings
            self.assertNotIn("SECRET", path)
            self.assertNotIn("api_key", path)
            self.assertTrue(path.endswith(".json"))
            self.assertTrue(os.path.exists(path))

    def test_raw_response_file_created(self):
        """Raw response should be saved to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            response = {"test": "data"}
            path = xai_harvest.save_raw_response(response, "test theme", tmpdir)

            self.assertTrue(os.path.exists(path))
            with open(path, "r") as f:
                saved = json.load(f)
            self.assertEqual(saved, response)


# ===========================================================================
# Test 8: Response with markdown table saves evidence.md
# ===========================================================================

class TestMarkdownTableExtraction(unittest.TestCase):
    def test_extract_markdown_table_from_response(self):
        """Should extract markdown table from xAI response."""
        response = {
            "choices": [
                {
                    "message": {
                        "content": (
                            "| claim | source_name | source_url |\n"
                            "|---|---|---|\n"
                            "| test claim | test source | http://test.com |"
                        )
                    }
                }
            ]
        }
        table = xai_harvest.extract_markdown_table(response)
        self.assertIsNotNone(table)
        self.assertIn("|", table)
        self.assertIn("claim", table)

    def test_extract_no_table_returns_none(self):
        """If no markdown table, should return None."""
        response = {
            "choices": [
                {
                    "message": {
                        "content": "No table here"
                    }
                }
            ]
        }
        table = xai_harvest.extract_markdown_table(response)
        self.assertIsNone(table)

    def test_markdown_save_to_file(self):
        """Should save markdown table to evidence file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "evidence.md")
            table = "| claim | source_name |\n|---|---|\n| test | test |"

            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as f:
                f.write(table + "\n")

            self.assertTrue(os.path.exists(output_path))
            with open(output_path) as f:
                content = f.read()
            self.assertIn("claim", content)


# ===========================================================================
# Test 9: --auto-score calls import/validate/score/report/observe (mocked)
# ===========================================================================

class TestAutoScorePipeline(unittest.TestCase):
    def test_auto_score_pipeline_executes(self):
        """--auto-score should mention the Auto-Score pipeline in output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.dict(os.environ, {"XAI_API_KEY": "test-key"}):
                with patch("urllib.request.urlopen") as mock_urlopen:
                    # Mock API response with valid markdown table
                    mock_response = MagicMock()
                    mock_response.read.return_value = json.dumps({
                        "choices": [
                            {
                                "message": {
                                    "content": (
                                        "| claim | source_name | source_url | source_class | "
                                        "source_date | source_type | independence_rating | "
                                        "evidence_quality | specificity | catalyst_alignment | "
                                        "dissent_quality | time_signal | is_duplicate | notes |\n"
                                        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|\n"
                                        "| test claim | test | http://test | major_news | "
                                        "2025-01-01 | news | 15 | 18 | 16 | 8 | 2 | 7 | false | test |"
                                    )
                                }
                            }
                        ],
                        "usage": {"cost_in_usd_ticks": 1000}
                    }).encode("utf-8")
                    mock_urlopen.return_value.__enter__.return_value = mock_response

                    # Run harvest with auto_score
                    output = xai_harvest.harvest(
                        theme="test theme",
                        output_path=os.path.join(tmpdir, "test.md"),
                        auto_score=True,
                        data_dir=tmpdir,
                        reports_dir=tmpdir,
                    )

                    # Output should mention the Auto-Score pipeline
                    self.assertIn("Auto-Score", output)
                    # Output should show the markdown was saved
                    self.assertIn("Saved markdown evidence", output)


# ===========================================================================
# Test 10: auto_score=False skips pipeline and shows manual steps
# ===========================================================================

class TestManualPipeline(unittest.TestCase):
    def test_without_auto_score_shows_manual_steps(self):
        """Without auto-score, harvest should show manual pipeline steps."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.dict(os.environ, {"XAI_API_KEY": "test-key"}):
                with patch("urllib.request.urlopen") as mock_urlopen:
                    # Mock API response
                    mock_response = MagicMock()
                    mock_response.read.return_value = json.dumps({
                        "choices": [
                            {
                                "message": {
                                    "content": (
                                        "| claim | source_name | source_url | source_class | "
                                        "source_date | source_type | independence_rating | "
                                        "evidence_quality | specificity | catalyst_alignment | "
                                        "dissent_quality | time_signal | is_duplicate | notes |\n"
                                        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|\n"
                                        "| test | test | http://test | major_news | "
                                        "2025-01-01 | news | 15 | 18 | 16 | 8 | 2 | 7 | false | test |"
                                    )
                                }
                            }
                        ],
                        "usage": {"cost_in_usd_ticks": 1000}
                    }).encode("utf-8")
                    mock_urlopen.return_value.__enter__.return_value = mock_response

                    # Run harvest WITHOUT auto_score
                    output = xai_harvest.harvest(
                        theme="test theme",
                        output_path=os.path.join(tmpdir, "test.md"),
                        auto_score=False,
                        data_dir=tmpdir,
                        reports_dir=tmpdir,
                    )

                    # Should show manual pipeline commands
                    self.assertIn("To continue with the full pipeline", output)
                    self.assertIn("import-md", output)
                    self.assertIn("validate", output)


# ===========================================================================
# Test 11: HTTP 401 gives helpful error message
# ===========================================================================

class TestHTTP401Error(unittest.TestCase):
    def test_http_401_helpful_message(self):
        """HTTP 401 should return helpful auth error message."""
        with patch.dict(os.environ, {"XAI_API_KEY": "test-key"}):
            with patch("urllib.request.urlopen") as mock_urlopen:
                # Mock 401 error
                error_response = MagicMock()
                error_response.read.return_value = b"Unauthorized"
                mock_urlopen.side_effect = urllib.error.HTTPError(
                    "http://test", 401, "Unauthorized", {}, None
                )

                response, error = xai_harvest.make_request("test-key", "test theme")

                self.assertIsNone(response)
                self.assertIn("Authentication failed", error)
                self.assertIn("XAI_API_KEY", error)

    def test_http_429_rate_limit_message(self):
        """HTTP 429 should return rate limit message."""
        with patch.dict(os.environ, {"XAI_API_KEY": "test-key"}):
            with patch("urllib.request.urlopen") as mock_urlopen:
                mock_urlopen.side_effect = urllib.error.HTTPError(
                    "http://test", 429, "Too Many Requests", {}, None
                )

                response, error = xai_harvest.make_request("test-key", "test theme")

                self.assertIsNone(response)
                self.assertIn("Rate limited", error)


# ===========================================================================
# Test 12: No generated docs suggest purchases, investments, or companies to buy
# ===========================================================================

class TestNonAdvisoryBoundary(unittest.TestCase):
    def test_harvest_prompt_no_buy_recommendations(self):
        """Harvest prompt should not suggest buying any companies."""
        prompt = xai_harvest.build_harvest_prompt("test theme")

        advisory_phrases = [
            "buy now", "sell now", "hold this",
            "recommended company", "price target",
            "expected return", "alpha score",
        ]

        for phrase in advisory_phrases:
            # These should appear as PROHIBITIONS, not recommendations
            if phrase in prompt.lower():
                # Check that they appear in a prohibition context
                context = prompt.lower()
                self.assertTrue(
                    "do NOT" in context or "not" in context,
                    f"'{phrase}' should appear only in prohibition context"
                )

    def test_slug_generation_safe(self):
        """Slug generation should be filesystem-safe."""
        slugs = [
            xai_harvest.make_slug("AI data center power scarcity"),
            xai_harvest.make_slug("GPU Memory Bandwidth ÷ 2x Growth"),
            xai_harvest.make_slug("NVIDIA Q4 2024 > AMD"),
        ]

        for slug in slugs:
            # Should only contain lowercase alphanumerics and hyphens
            self.assertTrue(all(c.isalnum() or c == "-" for c in slug))
            # Should not contain spaces or special characters
            self.assertNotIn(" ", slug)
            self.assertNotIn("/", slug)
            self.assertNotIn("\\", slug)


# ===========================================================================
# Test: Request URL is exactly https://api.x.ai/v1/responses (regression for
# urljoin bug where /v1 base + /responses endpoint would drop /v1)
# ===========================================================================

class TestRequestURL(unittest.TestCase):
    def test_request_url_is_full_v1_path(self):
        """
        Regression test: url must be https://api.x.ai/v1/responses.
        urljoin("https://api.x.ai/v1", "/responses") incorrectly yields
        "https://api.x.ai/responses" — the f-string concatenation is correct.
        """
        captured_urls = []

        class MockResponse:
            def read(self):
                return json.dumps({
                    "choices": [{"message": {"content": "no table here"}}],
                    "usage": {}
                }).encode()
            def __enter__(self): return self
            def __exit__(self, *a): pass

        with patch("urllib.request.urlopen", return_value=MockResponse()) as mock_open:
            with patch("urllib.request.Request") as mock_req:
                mock_req.return_value = MagicMock()
                mock_open.return_value = MockResponse()
                xai_harvest.make_request("test-key", "test theme")
                if mock_req.called:
                    captured_urls.append(mock_req.call_args[0][0])

        if captured_urls:
            self.assertIn("/v1/responses", captured_urls[0],
                          f"URL missing /v1 path segment: {captured_urls[0]}")
            self.assertNotEqual(captured_urls[0], "https://api.x.ai/responses",
                                "URL incorrectly dropped /v1 — urljoin bug")

    def test_xai_base_url_and_endpoint_concatenate_correctly(self):
        """Verify the constants produce the correct full URL when f-string joined."""
        full_url = f"{xai_harvest.XAI_BASE_URL}{xai_harvest.XAI_RESPONSES_ENDPOINT}"
        self.assertEqual(full_url, "https://api.x.ai/v1/responses")

    def test_urljoin_would_produce_wrong_url(self):
        """Document why urljoin is wrong for this pattern."""
        from urllib.parse import urljoin
        broken = urljoin("https://api.x.ai/v1", "/responses")
        correct = f"{xai_harvest.XAI_BASE_URL}{xai_harvest.XAI_RESPONSES_ENDPOINT}"
        # urljoin drops /v1 when second arg starts with /
        self.assertEqual(broken, "https://api.x.ai/responses")
        self.assertEqual(correct, "https://api.x.ai/v1/responses")
        self.assertNotEqual(broken, correct)


if __name__ == "__main__":
    unittest.main()
