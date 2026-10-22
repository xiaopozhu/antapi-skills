# Release artifact contract

## Folder and identity

Recommended local location in AntAPI: `build/api-releases/<product>/vX.Y.Z/`. This is generated output, outside source checkouts used by the client builders, and excluded from Git. The folder is a handoff directory, not a new Admin upload format.

```text
v1.2.0/
  release.json
  swagger.json
  CHANGELOG.md
  ADMIN.md
  SHA256SUMS
  cli/                 # exact CLI builder output, if changed
  skills/              # exact Skills packager output, if changed
  evidence/            # mutable execution/activation records; excluded from sealed identity
```

Use independent repository versions. An example identity (values are placeholders, never execution evidence):

```json
{
  "schema_version": 1,
  "product": "whois",
  "api_version": "1.2.0",
  "api_major": "v1",
  "selected_tags": ["WHOIS"],
  "source": {"repo": "xiaopozhu/antapi", "commit": "<40-lowercase-hex>"},
  "swagger": {"path": "swagger.json", "sha256": "<64-lowercase-hex>"},
  "clients": {
    "cli": {"repo": "xiaopozhu/antapi-cli", "version": "v0.1.0", "commit": "<40-lowercase-hex>", "mode": "build"},
    "skills": {"repo": "xiaopozhu/antapi-skills", "version": "v0.1.0", "commit": "<40-lowercase-hex>", "mode": "build"}
  }
}
```

`mode` is `build` or `reuse`. For reuse, also record the verified Release URL and immutable asset manifest digest. API major denotes the Gateway path contract, not the product's patch release. Do not invent production Catalog Release IDs, Price Version IDs, prices or deployment status. Tags and versions must come from the requested release and actual repository facts.

Resolve all source changes before sealing: generation, client command updates, Skill references, version files, validation and any source publication. The final remote source SHA may differ from a temporary local commit created via GitHub APIs. Build/package from the final clean source and record that SHA. Never mark dirty or `uncommitted` output as a publishable candidate.

## Public Swagger

From the AntAPI checkout, inspect annotations and regenerate:

```bash
zero swag --app own-api
go run ./scripts/api-release-export \
  --document cmd/own-api/docs/swagger.json \
  --product whois --version v1.2.0 --tag WHOIS \
  --out build/api-releases/whois/v1.2.0/swagger.json
```

Create the parent folder first. Repeat `--tag` for each explicitly selected tag. The exporter reuses `internal/catalog.PrepareOpenAPI`: controlled Gateway paths, Platform AK Bearer authentication, local schema references and bounded JSON; it excludes internal request headers, source servers and unselected operations. It emits **OpenAPI 3.0.3**, despite the conventional filename `swagger.json`, and rejects existing output files. If this exporter is absent, stop public-contract publication and report the missing prerequisite; do not replace it with regex header deletion.

Review parameter/schema examples and descriptions for secrets or internal material too; normalization is not a universal content redactor. Reimport using the same Catalog parser and selected tags; compare method/path, serialization and response schemas. Keep under Admin's 1 MiB input limit. No credentials belong in the release folder.

## Client artifacts

Inspect scripts before executing; interfaces can evolve. Current entrypoints:

```bash
# antapi-cli checkout; output must be outside this checkout
bash scripts/build-release.sh v0.1.0 <FULL_COMMIT_SHA> <ABSOLUTE_OUTPUT>/cli

# antapi-skills checkout; use its pinned official validator
make check-release SKILLS_REF=<PATH_TO_SKILLS_REF>
python3 scripts/package_skills.py --version 0.1.0 \
  --commit <FULL_COMMIT_SHA> --output <ABSOLUTE_OUTPUT>/skills
```

CLI needs the Go version in its `go.mod`, a clean exact source commit, five platform archives plus `manifest.json` and `SHA256SUMS`. Verify all hashes, archive member paths and native `version --json`; compare actual version/build commit with the manifest. Cross-compilation does not prove runtime operation on every OS.

Skills packaging includes **all** independent Skill directories in the final source commit. If this maintainer skill is part of the release, first ensure it is actually in that commit; do not copy it into output while claiming an earlier source SHA. Verify every manifest entry/hash and isolated archive; do not assume one package or reuse an older coordinator's single-WHOIS manifest gate. The packager only records the supplied `--commit`; it does not prove source identity. Use a fresh exact checkout, compare `git rev-parse HEAD` with the chosen SHA, require a clean tree including no untracked Skill files, and compare the Skill directory inventory with the commit tree. The packager may overwrite output, so build only into a fresh candidate directory, then freeze it. Validate installation from an isolated local path/archive. Product Skills must reference supported commands, CLI ranges and public API major. This maintainer skill depends on `gh` and the source builders, not on consumer CLI authentication.

A changed contract may need no CLI change, but document why. Current WHOIS CLI supports lookup and TLD listing; do not describe batch/poll/status commands unless implemented and verified. Test client updates against fixtures of both active and candidate contracts before choosing stable-before-Admin.

## Seal and resume

Write changelog from actual source differences: Added, Changed, Fixed, Breaking changes and upgrade requirements as relevant; no fabricated improvements. `ADMIN.md` lists chosen tags, routes, compatible clients, deployment prerequisite and manual checklist. Keep audit reason short and separate.

Generate sorted SHA-256 entries for every regular file recursively except `SHA256SUMS` and `evidence/`; include `release.json` and component manifests. Reject symlinks and paths escaping the release root. Freeze only after all source SHAs, versions and files are final. Verify the **exact file set**, not only listed hashes, before uploads/resume. Never regenerate checksums to bless unexplained drift. Changes require a fresh candidate folder; remote tag/version conflicts require an unused version chosen within the task's authorization.

Record progress in `evidence/` with UTC timestamps, command/run IDs, local/remote hashes, Release URLs and draft/public state. A write timeout is unknown until remote facts are reread. The evidence directory is not a sealed deliverable and must contain no credentials or full API request/response bodies. Record Admin activation separately using actual Catalog identity and verification results. No rollback or history rewrite on partial publication.
