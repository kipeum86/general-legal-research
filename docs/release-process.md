# Release Process

This project keeps three release surfaces in sync:

1. local release notes under `docs/releases/vX.Y.Z.md`
2. the `README.md` latest-release link
3. the Git tag and optional GitHub release body

Run the local preflight before publishing:

```bash
python3 scripts/release.py validate vX.Y.Z --require-tag-at-head
```

For an already-published historical release where the tag does not point at the current working commit, omit `--require-tag-at-head`:

```bash
python3 scripts/release.py validate v1.1.0
```

To generate the body for a GitHub release from the local note:

```bash
python3 scripts/release.py body vX.Y.Z
```

If a GitHub release body has been exported to a file, compare it to the local note:

```bash
python3 scripts/release.py validate vX.Y.Z --github-body-file /tmp/github-release-body.md
```

## Required Checks

- `docs/releases/vX.Y.Z.md` exists.
- The release note starts with `# vX.Y.Z`.
- `README.md` points to `docs/releases/vX.Y.Z.md` as the latest release.
- The Git tag `vX.Y.Z` exists.
- With `--require-tag-at-head`, the tag points to the current commit.
- With `--github-body-file`, the exported GitHub release body matches the local release note after trailing-space normalization.

## 한국어 요약

릴리즈 전에는 `scripts/release.py validate vX.Y.Z --require-tag-at-head`를 실행해 local release note, README latest link, Git tag가 같은 버전을 가리키는지 확인합니다. GitHub release body는 local release note를 그대로 쓰는 것을 원칙으로 하며, 이미 생성된 body 파일은 `--github-body-file`로 비교할 수 있습니다.
