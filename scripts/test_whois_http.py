"""离线验证独立 Skill 的 HTTP、凭据和失败边界。"""

import contextlib
import importlib.util
import io
import json
import os
import sys
from pathlib import Path
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError

MODULE = Path(__file__).resolve().parents[1] / "skills/antapi-whois/scripts/whois.py"
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("whois_http", MODULE)
whois = importlib.util.module_from_spec(spec)
spec.loader.exec_module(whois)


class Response(io.BytesIO):
    status = 200
    headers = {"X-Request-ID": "fixture-request", "X-AntAPI-Receipt-ID": "9007199254740993"}

    def __init__(self, body=None):
        super().__init__(body if body is not None else json.dumps({"code": 0, "data": {"registration": {"registered": True}}, "error": ""}).encode())


class HttpTests(unittest.TestCase):
    def invoke(self, args, response=None, error=None, env=None):
        stdout, stderr = io.StringIO(), io.StringIO()
        with patch.dict(os.environ, env or {"ANTAPI_KEY": "fixture-key", "ANTAPI_GATEWAY_URL": "https://gateway.example.test"}, clear=True), patch.object(whois, "open_request", side_effect=error, return_value=response or Response()) as request, contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            result = whois.main(args)
        return result, stdout.getvalue(), stderr.getvalue(), request

    def test_lookup_works_without_cli_and_preserves_ids(self):
        code, output, diagnostics, request = self.invoke(["lookup", "例子.中国"])
        self.assertEqual(code, 0)
        self.assertEqual(diagnostics, "")
        self.assertEqual(request.call_count, 1)
        argument = request.call_args.args[0]
        self.assertEqual(argument.full_url, "https://gateway.example.test/whois/v1/domains/xn--fsqu00a.xn--fiqs8s")
        self.assertEqual(argument.get_header("Authorization"), "Bearer fixture-key")
        self.assertEqual(json.loads(output)["metadata"]["receipt_id"], "9007199254740993")

    def test_missing_credentials_never_sends_request(self):
        code, output, diagnostics, request = self.invoke(["lookup", "example.com"], env={"ANTAPI_GATEWAY_URL": "https://gateway.example.test"})
        self.assertEqual(code, 1)
        self.assertEqual(output, "")
        self.assertIn("ANTAPI_CONFIGURATION_ERROR", diagnostics)
        request.assert_not_called()

    def test_unsafe_origins_and_domain_inputs_are_rejected_before_request(self):
        for origin in ["http://gateway.example.test", "https://user:pass@gateway.example.test", "https://gateway.example.test/path", "https://gateway.example.test?secret=fixture-key"]:
            with self.subTest(origin=origin):
                code, output, diagnostics, request = self.invoke(["lookup", "example.com"], env={"ANTAPI_KEY": "fixture-key", "ANTAPI_GATEWAY_URL": origin})
                self.assertEqual(code, 1)
                self.assertNotIn("fixture-key", output + diagnostics)
                request.assert_not_called()
        for domain in ["https://example.com/path", "example.com/$(touch /tmp/nope)", "-invalid.com"]:
            with self.subTest(domain=domain):
                code, _, _, request = self.invoke(["lookup", domain])
                self.assertNotEqual(code, 0)
                request.assert_not_called()

    def test_timeout_does_not_retry_or_expose_credentials(self):
        code, output, diagnostics, request = self.invoke(["lookup", "example.com"], error=URLError("fixture-key"))
        self.assertEqual(code, 1)
        self.assertEqual(request.call_count, 1)
        self.assertEqual(output, "")
        self.assertIn("ANTAPI_NETWORK_ERROR", diagnostics)
        self.assertNotIn("fixture-key", diagnostics)

    def test_redirect_and_platform_error_do_not_expose_body_or_retry(self):
        for status, body in [(302, b"fixture-key"), (503, b'{"code":1105,"data":null,"error":"fixture-key"}')]:
            with self.subTest(status=status):
                error = HTTPError("https://gateway.example.test", status, "unsafe", {"X-Request-ID": "fixture-error"}, io.BytesIO(body))
                code, output, diagnostics, request = self.invoke(["lookup", "example.com"], error=error)
                self.assertEqual(code, 1)
                self.assertEqual(request.call_count, 1)
                self.assertEqual(output, "")
                self.assertNotIn("fixture-key", diagnostics)
                self.assertIn("http_status=" + str(status), diagnostics)
                if status == 503:
                    self.assertIn("api_code=1105", diagnostics)

    def test_oversized_and_invalid_success_are_rejected(self):
        for body in [b"x" * (1024 * 1024 + 1), b"not JSON", b'{"code":true,"data":{}}', b'{"code":0,"data":null}']:
            with self.subTest(size=len(body)):
                code, output, diagnostics, _ = self.invoke(["lookup", "example.com"], response=Response(body))
                self.assertEqual(code, 1)
                self.assertEqual(output, "")
                self.assertIn("ANTAPI_INVALID_RESPONSE", diagnostics)

    def test_coverage_does_not_make_a_domain_lookup(self):
        code, _, _, request = self.invoke(["tlds"])
        self.assertEqual(code, 0)
        self.assertEqual(request.call_args.args[0].full_url, "https://gateway.example.test/whois/v1/tlds")

    def test_credential_echo_is_redacted_and_large_atoms_stay_strings(self):
        response = Response(b'{"code":0,"data":{"notice":"fixture-key"}}')
        response.headers = {"X-Request-ID": "fixture-key", "X-AntAPI-Credits-Debit-Atoms": "9007199254740995"}
        code, output, diagnostics, _ = self.invoke(["lookup", "example.com"], response=response)
        self.assertEqual(code, 0)
        self.assertNotIn("fixture-key", output + diagnostics)
        self.assertEqual(json.loads(output)["metadata"]["credits_debit_atoms"], "9007199254740995")

    def test_loopback_http_requires_explicit_development(self):
        env = {"ANTAPI_KEY": "fixture-key", "ANTAPI_GATEWAY_URL": "http://127.0.0.1:19876"}
        code, _, _, request = self.invoke(["lookup", "example.com"], env=env)
        self.assertEqual(code, 1)
        request.assert_not_called()
        env["ANTAPI_DEVELOPMENT"] = "1"
        self.assertEqual(self.invoke(["lookup", "example.com"], env=env)[0], 0)

    def test_no_redirect_handler_blocks_following(self):
        handler = whois.NoRedirect()
        self.assertIsNone(handler.redirect_request(None, None, 302, "Found", {}, "https://attacker.example.test"))


if __name__ == "__main__":
    unittest.main()
