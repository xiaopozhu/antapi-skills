# GitHub CLI publishing

All remote operations use `gh`. Follow the installed CLI's help and actual repository configuration. Do not print tokens. Scope every command to its explicit `OWNER/REPO`. Local Git may inspect, archive or prepare a clean checkout; it must not write remote refs. Do not silently run the old Docker/coordinator entrypoint as an implementation of this skill.

## Inspect

```bash
gh repo view OWNER/REPO --json nameWithOwner,defaultBranchRef
gh api repos/OWNER/REPO/git/ref/heads/main
gh workflow list --repo OWNER/REPO
gh workflow view WORKFLOW --repo OWNER/REPO --yaml
gh release view vX.Y.Z --repo OWNER/REPO --json tagName,isDraft,isPrerelease,targetCommitish,url,assets
gh api repos/OWNER/REPO/git/ref/tags/vX.Y.Z
```

An annotated tag returns a tag object: resolve it through `gh api repos/OWNER/REPO/git/tags/OBJECT_SHA`, following nested tag objects until a commit, and compare the full commit SHA. `targetCommitish` is not tag resolution. Distinguish an actual HTTP 404 from authentication/network failures; failure is not proof of absence.

Current CLI CI supports main push/PR/manual verification and has no tag publication trigger. Skills CI also validates rather than publishes. Recheck these facts instead of assuming they remain true forever.

## Publish source updates when authorized

Prefer a reviewable branch/PR and honor repository protection. `gh pr create` does not upload local Git commits. Use GitHub's Git database APIs through `gh api`:

1. Read the base ref and its commit/tree. Compute the exact source diff, excluding credentials, generated release folders and unrelated changes.
2. POST changed blobs to `repos/OWNER/REPO/git/blobs` with explicit base64 encoding. POST a tree to `.../git/trees` using `base_tree` and exact path/mode/type/SHA entries; deletion uses a null SHA. Preserve executable modes, reject unintended symlinks.
3. POST `.../git/commits` with the new tree and the observed base commit as its parent. Use the repository's commit-message convention. Save JSON request bodies to temporary files and pass `gh api --input FILE`; do not interpolate changelogs into shell commands.
4. Create a new branch using POST `.../git/refs` (`ref: refs/heads/BRANCH`, `sha: NEW_COMMIT`). If advancing an already-owned branch is necessary, reread it, require the expected parent and PATCH its ref with `force: false`; stop on divergence.
5. Create/check the PR with `gh pr create --body-file FILE`, `gh pr checks`. Merge only within existing authorization using `gh pr merge --match-head-commit SHA`; never bypass required checks/protection. An explicit authorized direct-main update may use the same non-force API after checks.

Read the resulting GitHub commit back. Use `gh repo clone OWNER/REPO TEMP_CHECKOUT -- --no-checkout`, then local `git checkout --detach FULL_SHA` and verify clean `git status` and `git rev-parse HEAD`. Use a fresh clone after merging so the final source commit is present. If a requested commit is unreachable or absent, resolve that repository state through `gh`; do not synthesize a different local commit and label it with the remote SHA. Builders that do not need Git metadata may instead consume `gh api repos/OWNER/REPO/tarball/FULL_SHA`. Do not publish source merely because preparation was requested.

## Build and verify

When a suitable release workflow exists, inspect its trigger, source ref, declared inputs, publisher and asset names. Dispatch with `gh workflow run WORKFLOW --repo OWNER/REPO --ref TAG_OR_BRANCH` and only real inputs. Confirm the resulting run's full `headSha`, event and workflow; use `gh run view`, `gh run watch --exit-status` and `gh run download` for that specific run. A manual dispatch request or green unrelated CI run does not establish publication success.

If no suitable workflow exists, use the documented local builders, then publish their frozen output through `gh`. If the user explicitly requires tag-triggered builds, report/configure that workflow as a separate authorized change before claiming this mode works. Do not equate `gh release create` with compiling a CLI.

## Create or resume Releases

Use the frozen component tag and full source SHA. Check **both tag and Release** before creating anything. A matching existing tag is reusable; a mismatched tag blocks publication even if no Release exists.

```bash
gh release create vX.Y.Z --repo OWNER/REPO --target FULL_COMMIT_SHA \
  --draft --title 'vX.Y.Z' --notes-file NOTES_FILE
gh release upload vX.Y.Z ASSET_FILE --repo OWNER/REPO
```

`--target` may create a lightweight tag. A Draft Release hides the release page/assets from ordinary users but does not make public Git source/tags private. Use a public stable release before Admin only under the chosen compatibility policy; API activation remains pending. Stable publication uses the same verified artifacts, without rebuilding.

Before resuming, resolve the tag, inspect release state, and download every existing relevant asset with `gh release download` into a fresh verification directory. Require identical names, bytes and full manifest file set. Upload a missing asset only to a matching **draft owned by this release attempt**, with recorded provenance. A conflicting or incomplete public Release blocks automatic repair: do not mix commits, append a rebuilt archive, use `--clobber`, force a tag, delete/recreate, or change another release's assets. Report the mismatch and use a separately authorized unused version.

After upload, download into a fresh folder, verify exact asset names/checksums against the sealed candidate and component manifests, and record URLs plus actual draft/public state. A Release created with no verified artifacts is incomplete. On any ambiguous write failure, reread remote state before retrying; never blindly repeat mutations.

When the operator later confirms Admin activation, verify public Catalog contract and required compatibility evidence, then publish only the matching draft through `gh release edit TAG --repo OWNER/REPO --draft=false --latest` under the release authorization. Reverify release/tag/assets and record completion. Do not advertise stable installation or mark the API live on an unverified operator statement alone.

Official references: [GitHub CLI release creation](https://cli.github.com/manual/gh_release_create), [workflow dispatch](https://cli.github.com/manual/gh_workflow_run), [Git database API](https://docs.github.com/en/rest/git).
