# AntAPI Skills

[English](README.md) | [简体中文](README.zh-CN.md)

Official AntAPI product Skills for coding agents. Install a Skill on its own and let your agent call the product's HTTP API directly with your project key and Credits. The [AntAPI CLI](https://github.com/xiaopozhu/antapi-cli) is a separate, optional tool.

## Install independently

Obtain a verified release archive or an authorized source checkout. Copy the complete `skills/antapi-whois/` folder into your agent's Skills directory, including `SKILL.md`, `scripts/` and `references/`. No AntAPI CLI installation is needed. With a local checkout, you can also run:

```bash
npx skills add /absolute/path/to/antapi-skills --skill antapi-whois
```

Choose your coding agent when prompted. Add `-g` for a user-wide installation, or `--agent codex` to target Codex. To list available skills:

```bash
npx skills add /absolute/path/to/antapi-skills --list
```

This uses the npm-distributed [`skills` installer](https://github.com/vercel-labs/skills). The repository does not need its own npm registry package. Manual folder installation does not need Node.js.

**Current status:** this repository is private; its owner controls the public launch. A local checkout or candidate archive is not a stable public release. The WHOIS Skill candidate is `0.1.0`; production API and billing acceptance are pending. Stable public installation sources must be pinned to verified tags/commits or release archives.

### Product skill requirements

- A supported Node.js runtime for the installer; see its [installation documentation](https://github.com/vercel-labs/skills#install-a-skill).
- Python 3.9+ and network access; the bundled HTTP helper uses only Python standard-library modules and public API v1.
- Privately provisioned `ANTAPI_KEY` in your agent's execution environment. Never paste credentials into agent chat or command arguments. The Skill uses `https://api.antapi.dev` by default; optional `ANTAPI_GATEWAY_URL` is only needed to select another environment.

The Skill calls the API directly and does not check or install the separate CLI. Installing a Skill does not create an API key. `ANTAPI_KEY` matches HTTP API examples; the optional CLI uses `ANTAPI_API_KEY`.

## Available skills

| Skill | Purpose | API / runtime |
| --- | --- | --- |
| [`antapi-whois`](skills/antapi-whois/SKILL.md) | Domain registration details and TLD coverage | API v1; Python 3.9+; no CLI dependency |

Skills and bundled references are English. Code comments and engineering notes are Chinese; README files are available in both languages.

## Local validation

Structure and packaging checks require Python 3.9+ and Make. The pinned official format validator requires a separate Python 3.11+ environment:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-tools.txt
make verify SKILLS_REF=.venv/bin/skills-ref
make check-release SKILLS_REF=.venv/bin/skills-ref
```

[`skills-ref`](https://github.com/agentskills/agentskills/tree/69ef37e9424c0a7ea9dd2293b559e43ec8176379/skills-ref) is pinned to commit `69ef37e9424c0a7ea9dd2293b559e43ec8176379`. `make verify` runs structure/reference checks, packaging tests, and official format validation. `make check-release` additionally rejects an empty repository. An empty bootstrap fixture may pass basic checks, with nothing installable.

Use `make check` and `make test` for the basic checks. The structure checker rejects symlinks, special files, missing references, and Markdown/HTML references escaping an individual skill. It does not replace format validation or Agent behavior evaluation.

[`tests/whois-scenarios.json`](tests/whois-scenarios.json) defines offline tasks and acceptance criteria. A scenario file is not execution evidence; see [evaluation records and limits](tests/README.md) for the checks actually performed. Local CI does not establish production readiness.

## Candidate packages

```bash
python3 scripts/package_skills.py --output /tmp/antapi-skill-packages
```

The packager creates `<skill>-<version>.tar.gz`, `SHA256SUMS`, and `manifest.json`. Each archive contains its independent skill directory and all bundled references. Entry order, timestamps, permissions, and ownership are deterministic; identical inputs produce identical bytes.

The version defaults to `VERSION` and can be overridden with `--version`. `--commit` accepts a full SHA; omitting it explicitly records `uncommitted`. Packaging rejects empty repositories, symlinks, special files, escaping references, and output paths inside `skills/`. It does not install skills, commit code, or publish a stable release.

For isolated local testing, copy the complete `skills/antapi-whois/` directory into your agent's skills directory, or run:

```bash
npx skills add /absolute/path/to/antapi-skills --skill antapi-whois
```

Keep the bundled references. Verify checksums before manually extracting candidate archives.

## Repository layout

```text
skills/
  antapi-<product>/
    SKILL.md
    references/
    scripts/       # only when a workflow needs a helper
```

Organize skills around user tasks and products, following the [Agent Skills specification](https://agentskills.io/specification). Each directory must work independently, with no cross-skill relative dependencies. `SKILL.md` defines triggers, API/runtime compatibility, workflow, authorization bounds, interpretation, and recovery. WHOIS includes a bounded HTTP helper: one request, 30-second timeout, 1 MiB response cap, no redirects or retries, and no default body persistence.

## Releases

This repository contains customer-facing product skills only. Internal release, operations, and administrator skills belong in the private AntAPI project and are excluded from distribution.

All product skills share one repository version/tag. API, Skills and CLI releases are independent; each Skill declares its public API major and actual runtime requirements. Stable installation sources are pinned to verified tags/commits or archives. Local candidate installation does not publish anything. CI validates changes and does not automatically publish on push or tag.
