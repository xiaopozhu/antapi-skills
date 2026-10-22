# AntAPI Skills

[English](README.md) | [简体中文](README.zh-CN.md)

Official AntAPI product and maintainer skills for coding agents. Product skills use the official [AntAPI CLI](https://github.com/xiaopozhu/antapi-cli) to access the same platform APIs, API keys, and Credits.

## Install with `npx skills`

Run from your project directory:

```bash
npx skills add xiaopozhu/antapi-skills --skill antapi-whois
```

Choose your coding agent when prompted. Add `-g` for a user-wide installation, or `--agent codex` to target Codex. To list available skills:

```bash
npx skills add xiaopozhu/antapi-skills --list
```

This uses the npm-distributed [`skills` installer](https://github.com/vercel-labs/skills) to fetch skills from GitHub. The `antapi-skills` repository does not need its own npm registry package.

**Current status:** this command follows the repository's default branch and installs a development candidate. It is not a stable product release. The first WHOIS Skill candidate is `0.1.0`; production API and billing acceptance are pending. Stable installation sources will be pinned to verified tags/commits or release archives.

### Product skill requirements

- A supported Node.js runtime for the installer; see its [installation documentation](https://github.com/vercel-labs/skills#install-a-skill).
- Official AntAPI CLI, stable version `>=0.1.0 <1.0.0`, using public API v1.
- A locally configured Gateway profile and API key. Follow the CLI README; never paste credentials into agent chat.

The CLI's first stable release has not been published yet. Development CLI builds report `dev`, which the Skill rejects. Installing a Skill does not install the CLI or configure credentials.

## Available skills

| Skill | Purpose | CLI compatibility |
| --- | --- | --- |
| [`antapi-whois`](skills/antapi-whois/SKILL.md) | Domain registration details and TLD coverage | `>=0.1.0 <1.0.0` |
| [`antapi-release`](skills/antapi-release/SKILL.md) | Maintainer: prepare API release artifacts, synchronize client releases through `gh`, and hand off manual Admin activation | Source builders + `gh`; no consumer API key |

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

Organize skills around user tasks and products, following the [Agent Skills specification](https://agentskills.io/specification). Each directory must work independently, with no cross-skill relative dependencies. `SKILL.md` defines triggers, CLI/API compatibility, workflow, authorization bounds, interpretation, and recovery. HTTP, authentication, and retry behavior belong to the CLI.

## Maintainer release skill

```bash
npx skills add /absolute/path/to/antapi-skills --skill antapi-release
```

Use this local-source command while the new skill is unpublished. Once present on the target GitHub ref, replace the local path with `xiaopozhu/antapi-skills`. Invoke it with `$antapi-release` and the product/version to prepare. It creates a versioned handoff directory containing the public Swagger, changelog, source/version identity, checksums and client artifacts; remote operations use GitHub CLI. It does not need a consumer API key.

New endpoints awaiting Admin activation use candidate Draft Releases by default. An explicitly chosen stable client release must remain compatible with the active API. Docker deployment and Admin activation remain operator actions. Admin currently imports the Swagger JSON only; it does not accept a release bundle or store changelogs. The release skill requires AntAPI's `scripts/api-release-export` public-contract exporter.

## Coordinated releases

The repository uses one version/tag for all skills. The maintainer skill coordinates a frozen API release folder → CLI/Skills candidates or verified compatible releases → manual Admin activation. Versions are independent; unchanged clients reuse verified releases. This supersedes the earlier API-first coordinator order. See [the current runbook](https://github.com/xiaopozhu/antapi/blob/main/docs/ops/api-release-skill.md) and the skill's bundled references; locally prepared AntAPI changes must be available before those remote documentation/exporter paths can be used.

The default-branch install above previews product candidates. Stable sources must be pinned to verified tags/commits or archives. CI validates changes and does not automatically publish on push or tag. Packaging includes every skill directory, not only WHOIS.
