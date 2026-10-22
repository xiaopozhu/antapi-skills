# Failure and uncertain outcomes

On failure, stdout is empty. Read the exit status and stderr; do not parse failure as a successful JSON envelope.

| Exit / diagnostic | Interpretation and next step |
| --- | --- |
| `2` | Invalid invocation or input. Use a bare domain and supported command; inspect local help if needed. Do not echo unsafe input into a shell command. |
| `1`, `CLI_CONFIGURATION_ERROR` | Local configuration or credentials are unavailable/invalid. Ask the user to configure their Gateway and AK locally; do not request their AK in chat. |
| `1`, `CLI_NETWORK_ERROR` | Transport or timeout failure. Execution and final billing may be unknown; do not assert the request never ran or create a replacement paid operation automatically. |
| `1`, `CLI_INVALID_RESPONSE` | Bounded response validation failed. No trustworthy registration conclusion; preserve any supplied safe request ID for support. |
| `1`, `CLI_PLATFORM_ERROR` | HTTP or platform failure. The diagnostic may carry numeric `api_code` and `request_id`; report those exact values when useful. |
| `1`, `CLI_EXECUTION_FAILED` | Other local execution failure. Do not fabricate the cause or an API result. |

The CLI suppresses raw server error bodies. Use only available diagnostic information; a generic configuration/network error does not reveal a specific HTTP status.

The public WHOIS contract defines these lookup error codes. They are conditional interpretations when the CLI actually supplies that numeric `api_code`, not values to infer from wording:

| `api_code` | Meaning |
| --- | --- |
| `1100` | Invalid domain |
| `1101` | Unsupported TLD |
| `1102` | Upstream rate limited |
| `1103` | Upstream timeout |
| `1104` | Invalid upstream response |
| `1105` | Upstream unavailable |
| `1110` | TLD temporarily unavailable |
| `1112` | Internal WHOIS failure |

Gateway can also reject invalid AKs, insufficient Credits, conflicts, rate limits, and unavailable infrastructure. Do not invent their numeric codes. Platform errors are not evidence that a domain is unregistered. A successful `code: 0` with `data.registration.registered: false` is a normal lookup result.

Respect any existing quantity and cost authorization. Do not start a fresh paid operation merely to recover from timeouts or disconnects: the original request may have executed, and a new invocation may incur another charge. Report the uncertainty and use existing Console records or support with the safe request ID when available. This supported CLI has no original-operation status/recovery command. Never promise a final Debit, Release, refund, or zero cost without the corresponding authoritative fact.
