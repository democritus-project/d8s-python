# AGENTS.md

## Commit messages: use Conventional Commits

Releases are automated by [release-please](https://github.com/googleapis/release-please).
It reads commit messages to bump the version, write `CHANGELOG.md`, tag, and publish to
PyPI. **Non-conventional commits are silently ignored** — no version bump, absent from the
changelog.

Format: `type: description` (optionally `type(scope): description`).

Common types and their effect on the release:

| Type | Effect | Changelog section |
|------|--------|-------------------|
| `feat:` | minor bump (0.8.0 → 0.9.0) | Features |
| `fix:` | patch bump (0.8.0 → 0.8.1) | Bug Fixes |
| `perf:` | patch bump | Performance Improvements |
| `deps:` | no bump (rides next release) | Dependencies |
| `docs:` `refactor:` `test:` `chore:` `ci:` `build:` `style:` | no bump | hidden |

Breaking change: append `!` (`feat!: ...`) or add a `BREAKING CHANGE:` footer → major bump.

Examples:

```
feat: add iterable_chunk
fix: cycle() returns empty when length is 0
feat!: rename list_flatten to iterable_flatten
```

Prefer squash-merging PRs so the PR title becomes the single conventional commit.

## Releasing

Don't bump versions, edit `CHANGELOG.md`, or create tags by hand — release-please owns all
three. To cut a release, merge the open `chore: release X.Y.Z` PR; that tags the version,
creates the GitHub Release, and publishes to PyPI via OIDC.
