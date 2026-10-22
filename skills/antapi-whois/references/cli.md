# CLI contract

Supported official CLI: stable `>=0.1.0 <1.0.0`; public AntAPI API major: `v1`. The initial candidate version is `0.1.0`; this document does not assert that it has been published.

| Command | Purpose |
| --- | --- |
| `antapi version --json` | Local version preflight; no credentials or network needed |
| `antapi whois lookup example.com --json` | One domain registration lookup |
| `antapi whois tlds --json` | Current TLD coverage, protocols, and availability |
| `antapi --help` | Local command help |

`antapi version --json` returns an object with `version`, `commit`, and `built_at`. It does not use the API response envelope. A development build can report `dev`, which is outside this Skill's supported range.

Optional root flags go before `whois`: `--config PATH`, `--profile NAME`, `--gateway-url ORIGIN`, `--core-url ORIGIN`. For example, `antapi --profile work whois lookup example.com --json`. Keep a user's selected profile and deployment; do not invent a production hostname. WHOIS requests go only through the configured Gateway, never to Own API directly. `core_url` is not used for WHOIS calls.

Configuration defaults to `$XDG_CONFIG_HOME/antapi/config.json` when set, otherwise the operating system's user configuration directory under `antapi/`. It selects `default_profile` and `profiles` containing `gateway_url`, `core_url`, `development`, and `timeout_seconds`. HTTPS is required except explicit localhost/loopback development. Do not switch to development to work around a remote connection failure.

`ANTAPI_API_KEY` overrides the selected profile's entry in `credentials.json` beside the config file. That file must be a regular, non-symlink file with POSIX mode `0600`; Windows uses environment credentials. Have the user provision credentials locally through a private workflow. Do not request, display, or copy their value into chat or shell history. No AK flag or login command exists.

## Success output

Exit status `0` and one stdout JSON object mean HTTP 2xx and platform `code: 0`:

- `code`: platform numeric result code.
- `data`: the public API result, not a CLI-specific schema.
- `metadata.http_status`, plus `request_id`, `receipt_id`, and `credits_debit_atoms` when present. IDs and Credits atoms are strings; do not convert monetary values to floating point or infer absent billing metadata.

WHOIS lookup data is grouped under `domain` (`input`, `queried`, `unicode`), `registration` (`registered`), `record`, `quality`, and `source`. Optional record fields include `registrar.name`, `dates.registered_at`, `dates.expires_at`, `dates.updated_at`, `contacts`, `nameservers`, and `secure_dns`. Check actual field presence. `quality` includes `support_level`, `completeness`, and `warnings`; `source` includes `protocol`, `server`, `fetched_at`, `cache_hit`, and source/parser versions.

Coverage data contains `source_version`, `generated_at`, and `items`. Each item reports `tld`, `unicode_tld`, `support_level`, `availability`, `protocols`, `last_verified_at`, and optional `unsupported_reason`. Coverage availability is operational support, not domain registration availability.

## Request bounds

The CLI makes one request per invocation, does not automatically retry or follow redirects, defaults to a 30-second timeout (configured range 1–120 seconds), and caps responses at 1 MiB. It has no batch, polling, idempotency-key, or status command. Follow [error recovery](errors.md) for failures; a second invocation is a new operation whose cost cannot be assumed zero.
