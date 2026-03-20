# Contributing to `csv_detective`

Thank you for being willing to improve `csv_detective`!

Every modification should be submited as a PR (without touching the CHANGELOG, which is updated with the commits labels on release).

## Linting

Remember to format, lint, and sort imports with [Ruff](https://docs.astral.sh/ruff/) before committing (checks will remind you anyway):
```bash
pip install .[dev]
ruff check --fix .
ruff format .
```

### Doc generation

Before pushing, if any file in `csv_detective/formats/` has been touched, please run `python docs/generate_doc.py` to update `docs/formats.md`. A check in the CI will remind you.

### 🏷️ Release

The release process uses the [`tag_version.sh`](tag_version.sh) script to create git tags and update [CHANGELOG.md](CHANGELOG.md) and [pyproject.toml](pyproject.toml) automatically.

**Prerequisites**: [GitHub CLI](https://cli.github.com/) (`gh`) must be installed and authenticated, and you must be on the main branch with a clean working directory.

```bash
# Create a new release
./tag_version.sh <version>

# Example
./tag_version.sh 2.5.0

# Dry run to see what would happen
./tag_version.sh 2.5.0 --dry-run
```

The script automatically:
- Updates the version in `pyproject.toml`
- Extracts commits since the last tag and formats them for `CHANGELOG.md`
- Identifies breaking changes (commits with `!:` in the subject)
- Creates a git tag and pushes it to the remote repository
- Creates a GitHub release with the changelog content
