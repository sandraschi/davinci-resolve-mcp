# Branch Protection Rules

This document outlines the branch protection rules for the DaVinci Resolve MCP repository.

## Protected Branches

### `main` Branch
The `main` branch is the primary production branch and has the following protections:

#### Required Status Checks
All of the following must pass before merging:
- `test` - Unit and integration tests
- `lint` - Code quality checks (black, isort, flake8, mypy)
- `build` - Package building and validation

#### Branch Protection Settings
- ✅ Require pull request reviews before merging
- ✅ Require status checks to pass before merging
- ✅ Require branches to be up to date before merging
- ✅ Include administrators in restrictions
- ✅ Restrict pushes that create matching branches
- ✅ Allow force pushes: **Disabled**
- ✅ Allow deletions: **Disabled**

#### Review Requirements
- **Required reviewers**: 1
- **Dismiss stale pull request approvals**: Enabled
- **Require review from Code Owners**: Enabled
- **Restrict push access to authorized users**: Enabled

### `develop` Branch
The `develop` branch is used for ongoing development and has lighter protections:

#### Required Status Checks
- `test` - Unit and integration tests
- `lint` - Code quality checks

#### Branch Protection Settings
- ✅ Require pull request reviews before merging
- ✅ Require status checks to pass before merging
- ✅ Include administrators in restrictions
- ✅ Allow force pushes: **Disabled**
- ✅ Allow deletions: **Disabled**

#### Review Requirements
- **Required reviewers**: 1
- **Dismiss stale pull request approvals**: Enabled

## Branch Naming Convention

### Feature Branches
```
feature/description-of-feature
feature/JIRA-123-short-description
```

### Bug Fix Branches
```
fix/description-of-fix
fix/JIRA-123-short-description
```

### Documentation Branches
```
docs/description-of-docs
docs/update-api-reference
```

### Release Branches
```
release/v1.2.3
release/v1.2.3-rc.1
```

## Pull Request Process

### Creating Pull Requests
1. **Branch from**: `develop` for features, `main` for hotfixes
2. **Target branch**: `develop` for features, `main` for hotfixes
3. **Title format**: `[TYPE] Description of changes`
4. **Description**: Use the PR template

### Review Process
1. **Automated checks**: All CI/CD checks must pass
2. **Code review**: At least 1 reviewer approval required
3. **Testing**: Reviewer should verify changes work as expected
4. **Merge**: Use "Squash and merge" for clean history

### Release Process
1. **Create release branch** from `develop`
2. **Run full test suite** and validate
3. **Update version** in `pyproject.toml`
4. **Merge to `main`** via pull request
5. **Tag release** on `main`
6. **Deploy** via GitHub Actions

## Emergency Procedures

### Hotfixes
For critical production issues:
1. Create hotfix branch from `main`
2. Implement minimal fix
3. Test thoroughly
4. Merge directly to `main` (bypassing normal process)
5. Cherry-pick to `develop` if needed

### Rollbacks
If a release causes issues:
1. Create rollback PR reverting problematic changes
2. Fast-track through review process
3. Merge and deploy immediately

## Code Owners

The following users are designated as Code Owners and their approval is required for changes to critical files:

- `@sandraschieder` - All files
- Additional code owners can be added to `.github/CODEOWNERS`

## Enforcement

Branch protection rules are enforced automatically by GitHub. Attempts to bypass these rules (force pushes, direct merges, etc.) will be blocked.

### Exceptions
- Repository administrators can override protections in emergency situations
- Overrides should be documented and justified
- Regular bypasses indicate the rules need adjustment

## Monitoring

Branch protection effectiveness is monitored through:
- GitHub repository insights
- Pull request metrics
- Code quality metrics
- Deployment success rates

## Updates

This document should be updated when:
- Branch protection rules change
- New branches are added
- Process improvements are identified
- Security requirements evolve
