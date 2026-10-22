---
name: antapi-release
description: Prepare or publish an AntAPI own-api version with a versioned artifact folder, synchronize antapi-cli and antapi-skills through GitHub CLI, and hand off the public Swagger and changelog for manual Admin activation.
---

# AntAPI Release

Use a frozen API release folder to coordinate the three repositories. Publishing clients and activating the API are separate facts. This maintainer skill uses `gh`; it does not require the consumer AntAPI CLI or an API key.

## Prepare

1. Read each repository's instructions and current release tooling. Determine product, selected Swagger tags, API release version, source commits, and compatible CLI/Skills versions. Reuse unchanged verified components; the three versions need not match. Preserve unrelated working changes. Creating/updating this skill is not authorization to publish a product release.
2. Read [artifact contract](references/artifacts.md). Create a separate release folder with public `swagger.json`, user-facing `CHANGELOG.md`, immutable `release.json`, checksums and `ADMIN.md`. Generate Swagger from handler annotations, then use AntAPI's Catalog-based public exporter. Never publish raw own-api Swagger or substitute the currently active Catalog for the candidate contract.
3. Compare the candidate contract with the active API. Implement needed CLI commands and Skill instructions; Swagger alone does not create either. Verify command examples against the actual CLI. Build from exact clean commits using existing builders, validate every Skill, and test the combination offline. Record missing production checks honestly.

## Synchronize and publish

Read [GitHub procedure](references/github.md) before remote changes. **Use `gh` for remote repository, branch, commit, PR, tag, workflow, Release and asset operations.** Local Git inspection/builds are allowed; do not use `git push`, direct remote Git writes, or another provider's publishing tool.

Use existing release authorization without repeatedly asking. Preparing artifacts alone does not authorize public publishing. Do not commit/publish unrelated repositories or changes.

Inspect real workflows. A CI check is not a tag release workflow. Use an existing release workflow only if its triggers and outputs fit; otherwise run verified local builders and publish through `gh`. Do not add a workflow just to avoid reporting that it is missing.

For endpoints awaiting Admin activation, default to candidate **Draft Releases** and withhold stable installation recommendations. A public repository's tag/source may still be accessible. A compatible stable client may precede Admin only when explicitly chosen and verified against the active API. Never move an existing tag or replace published assets. On conflict, preserve evidence and stop that publication; continue independent local preparation.

## Hand off

Give artifact paths, exact source/version combinations, checksums, actual GitHub links and remaining checks. Finish at **ready for manual Admin** only after every required preparation/publication check passes; otherwise name the incomplete items.

Admin currently imports one Swagger/OpenAPI JSON, not a release bundle or changelog. Keep changelog alongside it; the audit reason is not changelog storage. The operator must confirm the required Docker backend is deployed, import the JSON, review routes/prices/limits, and activate using existing MFA/audit controls. Do not automate Admin, change billing, deploy Docker, or make billable smoke calls without task-specific authorization.

On a later resume, verify active public Catalog and client compatibility before promoting drafts or recommending stable installs. Record activation evidence separately; do not rewrite frozen release identity. Report API live only when activation is verified. Website rebuild after Catalog publication remains a separate follow-up.
