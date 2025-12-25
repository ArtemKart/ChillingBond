# Semantic Versioning Guidelines

This document outlines the versioning strategy for ChillingBond. We follow [Semantic Versioning 2.0.0](https://semver.org/) with automatic version bumping via GitHub Actions and [python-semantic-release](https://github.com/python-semantic-release/python-semantic-release).

## Version Format

Our version format follows: **MAJOR.MINOR.PATCH**

Example progression: `0.1.0` → `0.2.0` → `0.2.1` → `1.0.0`

---

## Git Flow

We use a standard Git Flow branching model with automatic versioning on releases to main:

```
feature branches → dev → release → main (automatic version bump & tag)
```

### Branch Structure

- **`feature/*`** - Individual feature branches created from `dev`
- **`dev`** - Development branch where features are integrated
- **`release`** - Release preparation branch created from `dev`
- **`main`** - Production branch where releases happen

### Workflow

1. **Feature Development**
   ```
   git checkout -b feature/your-feature dev
   # Make changes, commit with conventional commits
   git push origin feature/your-feature
   ```

2. **Merge to Dev**
   - Create Pull Request: `feature/your-feature` → `dev`
   - Review and merge

3. **Create Release**
   ```
   git checkout -b release/X.Y.Z dev
   # Final testing, version bumps if needed
   git push origin release/X.Y.Z
   ```

4. **Merge to Main (Automatic Version Bump)**
   - Create Pull Request: `release/X.Y.Z` → `main`
   - **Merge PR** → GitHub Actions workflow automatically:
     - Analyzes commits since last tag
     - Determines version bump type (patch, minor, major)
     - Updates `pyproject.toml`
     - Creates git tag `vX.Y.Z`
     - Creates GitHub Release
     - Updates `CHANGELOG.md`

---

## Automatic Version Determination

The GitHub Actions workflow uses `python-semantic-release` to **automatically determine** the version bump type based on **conventional commit messages** in the release.

### Conventional Commit Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Commit Types and Version Bumps

| Type | Bump | Use Case |
|------|------|----------|
| **feat** | MINOR | New feature |
| **fix** | PATCH | Bug fix |
| **perf** | NONE | Performance improvement |
| **docs** | NONE | Documentation updates |
| **style** | NONE | Code style changes (formatting, semicolons, etc.) |
| **refactor** | NONE | Code refactoring (no new functionality) |
| **test** | NONE | Test additions or modifications |
| **chore** | NONE | Build process, dependencies |

### Breaking Changes (MAJOR Bump)

Add `!` after type or include `BREAKING CHANGE:` footer to trigger **MAJOR** bump:

```
feat!: redesign authentication API

BREAKING CHANGE: Authentication endpoint moved from /auth to /api/v1/auth
```

### Commit Examples

```
feat: add payment processing system

Implements Stripe integration for bond purchases.
Adds new endpoints: POST /api/payments, GET /api/payments/{id}

fix: resolve race condition in authentication

Adds proper locking mechanism to prevent concurrent login attempts.

perf: optimize portfolio valuation queries

Reduces average query time from 500ms to 50ms using indexed views.

feat!: migrate to new API schema

BREAKING CHANGE: Investment object structure has changed.
Old format: { bondId, bondName }
New format: { id, name, type }
See migration guide: docs/MIGRATION_v1.md
```

---

## Version Bump Rules

### PATCH Bump (0.2.0 → 0.2.1)

Triggered by commits with types: `fix`

**Use when:**
- Bug fixes only
- Security patches
- Performance improvements

### MINOR Bump (0.1.0 → 0.2.0)

Triggered by commits with type: `feat` (without `!`)

**Use when:**
- New features added
- New backward-compatible functionality
- New API endpoints
- New integrations
- UX improvements

**Important:** All changes must be **backward compatible**.

### No Version Bump

Commits with these types do **NOT** trigger version bumps: `docs`, `style`, `refactor`, `test`, `chore`, 'perf'

**Use when:**
- Documentation updates (README, guides, comments)
- Code style or formatting changes
- Code refactoring without functional changes
- Test additions or modifications
- Build process or dependency updates
- Configuration changes
- Performance improvements

### MAJOR Bump (0.2.0 → 1.0.0)

Triggered by commits with:
- Type: `feat!` (with exclamation mark)
- Footer: `BREAKING CHANGE:`

**Use when:**
- Breaking API changes
- Incompatible modifications
- Removal of endpoints or features
- Major architectural changes
- Production-ready release (0.x.x → 1.0.0)

**Important:** Breaking changes must be clearly documented with migration guide.

---

## Automatic Release Process

### How It Works

1. **PR is merged from `release` → `main`**
2. **GitHub Actions workflow triggers automatically**
3. **Workflow analyzes commits** since last git tag
4. **Determines version bump** based on commit types:
   - Contains `feat!` or `BREAKING CHANGE:` → MAJOR
   - Contains `feat` → MINOR
   - Contains `fix` → PATCH
5. **Updates version** in `pyproject.toml`
6. **Creates git tag** `vX.Y.Z`
7. **Generates changelog** in `CHANGELOG.md`
8. **Creates GitHub Release** with version info

### Workflow Configuration

The workflow is configured in `.github/workflows/version-bump.yml` and uses `python-semantic-release` with settings in `pyproject.toml`:

```toml
[tool.semantic_release]
version_variable = "pyproject.toml:version"
changelog_file = "CHANGELOG.md"
commit_message = "chore: bump version to {version}"
tag_format = "v{version}"
```

---

## Example Release Scenarios

### Scenario 1: Multiple bug fixes and a new feature

**Commits in release branch:**
```
feat: add email notifications
fix: correct portfolio calculation
fix: resolve authentication timeout
perf: optimize database queries
docs: update API documentation
test: add notification tests
```

**Result:**
- Bump type: **MINOR** (because there's at least one `feat`)
- Version: 0.1.5 → 0.2.0
- Tag: `v0.2.0`
- Release created automatically
- Note: `docs` and `test` commits don't affect version bump

### Scenario 2: Only bug fixes and optimizations

**Commits in release branch:**
```
fix: resolve memory leak in connection pool
perf: improve API response time
fix: correct date formatting in reports
docs: add troubleshooting guide
refactor: simplify authentication logic
```

**Result:**
- Bump type: **PATCH** (only `fix` and `perf` count)
- Version: 0.2.0 → 0.2.1
- Tag: `v0.2.1`
- Release created automatically
- Note: `docs`, `refactor` and `perf` commits don't trigger version bump

### Scenario 3: Breaking changes for production release

**Commits in release branch:**
```
feat!: redesign authentication API
feat: update user dashboard
fix: resolve timezone issues
docs: add migration guide

BREAKING CHANGE: Authentication endpoint moved from /auth to /api/v1/auth
```

**Result:**
- Bump type: **MAJOR** (due to `feat!`)
- Version: 0.9.8 → 1.0.0
- Tag: `v1.0.0`
- Release created with migration guide
- Note: `docs` commits don't affect version bump

---

## Best Practices

### 1. Write Meaningful Commit Messages
```
✅ feat: add bond portfolio export functionality
✅ fix: resolve race condition in token refresh
❌ feat: stuff
❌ fix: bug
```

### 2. Use Correct Commit Types
```
✅ feat: new feature
✅ fix: bug fix
✅ perf: optimization
❌ feature: new feature (use "feat")
❌ bugfix: bug fix (use "fix")
```

### 3. Document Breaking Changes
```
✅ feat!: redesign API endpoints
   BREAKING CHANGE: Old endpoint removed, use new endpoint instead
   
❌ feat: breaking changes
   (without documenting what breaks)
```

### 4. Keep Commits Focused
```
✅ One logical change per commit
✅ Multiple commits for multiple features
❌ Multiple unrelated changes in one commit
```

### 5. Test Before Release
- Ensure all tests pass on `release` branch before merging to `main`
- Run full CI/CD pipeline
- Manual testing of critical features

### 6. Include Migration Guides for MAJOR Bumps
For breaking changes, provide:
- What changed
- Why it changed
- How to migrate old code
- Deprecation timeline (if applicable)

---

## Release Checklist

Before merging `release` branch to `main`:

1. ✅ All tests pass on `release` branch
2. ✅ All commits follow conventional commit format
3. ✅ No commits with just typos or "fix" without description
4. ✅ Breaking changes are documented
5. ✅ Migration guides are prepared (if MAJOR bump)
6. ✅ Code review completed
7. ✅ Final QA testing done

After merge to `main`:

1. ✅ GitHub Actions workflow completes successfully
2. ✅ `CHANGELOG.md` is updated correctly
3. ✅ GitHub Release is created with correct version
4. ✅ Git tag is created
5. ✅ Notify team about new release

---

## References

- [Semantic Versioning 2.0.0](https://semver.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [python-semantic-release Documentation](https://python-semantic-release.readthedocs.io/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Git Flow Model](https://nvie.com/posts/a-successful-git-branching-model/)
