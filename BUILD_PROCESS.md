# FaceFolio Build & Release Process

This document describes the standardized process for building, versioning, and releasing FaceFolio. Following these steps ensures consistency and quality for every release.

## 1. Versioning

FaceFolio uses [Semantic Versioning](https://semver.org/) (`vMajor.Minor.Patch`):

- **MAJOR** (`v1.x.x`): Increment for incompatible API changes or major feature overhauls.
- **MINOR** (`vx.1.x`): Increment for adding functionality in a backward-compatible manner.
- **PATCH** (`vx.x.1`): Increment for backward-compatible bug fixes.

## 2. Pre-Release Checklist

Before creating a new release, ensure the following:

- [ ] **Verify `main` Branch:** Confirm that the `main` branch is stable, fully tested, and contains all intended features and fixes.
- [ ] **Update `VERSION.md`:** Add a new section at the top for the new version. Document all significant changes, additions, and bug fixes.
- [ ] **Check Version Consistency:** Ensure the version number in `VERSION.md` (e.g., `## [v1.0.1]`) matches the Git tag you will create.

## 3. Creating a Release

The release process is automated via GitHub Actions. To trigger it:

**Create the Git Tag:**
```sh
git tag v1.0.1
```

**Push the Tag to GitHub:**
```sh
git push origin v1.0.1
```
_Alternatively, use `git push --tags` to push all new tags._

## 4. Post-Release Verification

After pushing the tag, the workflow will automatically:

- Build the `.exe` file.
- Create the installer.
- Publish a new release on GitHub with notes from `VERSION.md`.

**To verify the release:**

1. Go to the **Actions** tab in your GitHub repository to monitor the workflow.
2. Once complete, navigate to the **Releases** page.
3. Confirm the new release is published with the correct version, release notes, and the `FaceFolio_Setup_vX.Y.Z.exe` file attached for download.
