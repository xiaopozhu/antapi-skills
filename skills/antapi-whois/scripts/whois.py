"""独立 Skill 的有界 HTTP 调用；不依赖 AntAPI CLI，也不持久化正文或凭据。"""

import argparse
import json
import os
import re
import sys
from http.client import HTTPException
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

MAX_RESPONSE_BYTES = 1024 * 1024
TIMEOUT_SECONDS = 30


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def open_request(request):
    # 不跟随跳转、不重试；不把项目凭据发送给返回链接或环境代理。
    return build_opener(ProxyHandler({}), NoRedirect()).open(request, timeout=TIMEOUT_SECONDS)


def configuration():
    key = os.environ.get("ANTAPI_KEY", "")
    origin = os.environ.get("ANTAPI_GATEWAY_URL", "")
    parsed = urlsplit(origin)
    development = os.environ.get("ANTAPI_DEVELOPMENT") == "1"
    local = parsed.hostname in ("localhost", "127.0.0.1", "::1")
    if not key or len(key) > 8192 or any(ord(char) < 33 or ord(char) > 126 for char in key):
        raise ValueError("credentials")
    if not parsed.hostname or parsed.username is not None or parsed.password is not None or parsed.path not in ("", "/") or parsed.query or parsed.fragment:
        raise ValueError("origin")
    if parsed.scheme != "https" and not (parsed.scheme == "http" and local and development):
        raise ValueError("https")
    if parsed.port is not None and not 1 <= parsed.port <= 65535:
        raise ValueError("port")
    return origin.rstrip("/"), key


def domain_name(value):
    domain = value.rstrip(".").encode("idna").decode("ascii").lower()
    if len(domain) > 253 or not domain or not all(re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?", label) for label in domain.split(".")):
        raise ValueError("domain")
    return domain


def metadata(headers, status, key):
    result = {"http_status": status}
    for field, header, pattern in [("request_id", "X-Request-ID", r"[A-Za-z0-9._:-]{1,128}"), ("receipt_id", "X-AntAPI-Receipt-ID", r"[A-Za-z0-9._:-]{1,128}"), ("credits_debit_atoms", "X-AntAPI-Credits-Debit-Atoms", r"[0-9]{1,128}")]:
        value = headers.get(header, "")
        if value and key not in value and re.fullmatch(pattern, value):
            result[field] = value
    return result


def scrub(value, key):
    if isinstance(value, str):
        return value.replace(key, "[REDACTED]")
    if isinstance(value, list):
        return [scrub(item, key) for item in value]
    if isinstance(value, dict):
        return {scrub(name, key): scrub(item, key) for name, item in value.items()}
    return value


def reject_constant(value):
    raise ValueError("non-finite JSON")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Call AntAPI WHOIS through your configured Gateway; no CLI installation required.")
    parser.add_argument("operation", choices=("lookup", "tlds"))
    parser.add_argument("domain", nargs="?")
    try:
        args = parser.parse_args(argv)
    except SystemExit as error:
        return error.code
    if (args.operation == "lookup") != bool(args.domain):
        print("ANTAPI_INPUT_ERROR", file=sys.stderr)
        return 2
    try:
        domain = domain_name(args.domain) if args.domain else None
    except (ValueError, UnicodeError):
        print("ANTAPI_INPUT_ERROR", file=sys.stderr)
        return 2
    try:
        origin, key = configuration()
    except ValueError:
        print("ANTAPI_CONFIGURATION_ERROR", file=sys.stderr)
        return 1
    path = "/whois/v1/tlds" if domain is None else "/whois/v1/domains/" + quote(domain, safe="")
    request = Request(origin + path, headers={"Authorization": "Bearer " + key, "Accept": "application/json"}, method="GET")
    try:
        try:
            response = open_request(request)
        except HTTPError as error:
            response = error
        with response:
            status = response.status
            meta = metadata(response.headers, status, key)
            body = response.read(MAX_RESPONSE_BYTES + 1)
        if len(body) > MAX_RESPONSE_BYTES:
            raise ValueError("size")
        try:
            envelope = json.loads(body, parse_constant=reject_constant)
        except (ValueError, UnicodeError):
            if 200 <= status < 300:
                raise ValueError("json")
            envelope = None
        if not 200 <= status < 300 or isinstance(envelope, dict) and type(envelope.get("code")) is int and envelope["code"] != 0:
            details = " http_status=" + str(status)
            if isinstance(envelope, dict) and type(envelope.get("code")) is int:
                details += " api_code=" + str(envelope["code"])
            if meta.get("request_id"):
                details += " request_id=" + meta["request_id"]
            print("ANTAPI_PLATFORM_ERROR" + details, file=sys.stderr)
            return 1
        if not isinstance(envelope, dict) or type(envelope.get("code")) is not int or not isinstance(envelope.get("data"), dict):
            raise ValueError("envelope")
        print(json.dumps({"code": envelope["code"], "data": scrub(envelope["data"], key), "metadata": meta}, ensure_ascii=False))
        return 0
    except (URLError, OSError, HTTPException):
        print("ANTAPI_NETWORK_ERROR execution_and_billing_unknown", file=sys.stderr)
        return 1
    except (ValueError, UnicodeError, RecursionError):
        print("ANTAPI_INVALID_RESPONSE", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
