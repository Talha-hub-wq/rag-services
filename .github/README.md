# CI/CD Workflows

This directory contains GitHub Actions workflows for continuous integration, testing, security scanning, and deployment.

## Workflows

### [tests.yml](.workflows/tests.yml)
**Main CI/CD Pipeline**
- Runs on: Every push to `main`/`develop`, all pull requests
- Jobs:
  - Test: Unit tests on Python 3.9, 3.10, 3.11
  - Build: Docker image build and push to GHCR
  - Security: Trivy and Bandit scanning
  - Quality: Code quality analysis
  - Dependencies: Security vulnerability checks

### [deploy.yml](.workflows/deploy.yml)
**Deployment to Azure**
- Runs on: Push to `main` branch
- Requires: All tests passing
- Deploys: Backend and Frontend to Azure Container Instances

### [pr-checks.yml](.workflows/pr-checks.yml)
**Pull Request Validation**
- Runs on: All pull requests, pushes to main/develop
- Checks:
  - PR title format (conventional commits)
  - Code formatting (Black, isort, pylint)
  - Type checking (mypy)
  - Test coverage minimum (70%)
  - Dependency vulnerabilities
  - Documentation

### [scheduled.yml](.workflows/scheduled.yml)
**Scheduled Maintenance**
- Runs on: Daily at 2 AM UTC
- Jobs:
  - Dependency updates (auto-create PR)
  - Nightly tests on all Python versions
  - Security scanning
  - Docker image caching
  - Performance benchmarks
  - Code quality metrics

### [release.yml](.workflows/release.yml)
**Release Management**
- Runs on: Git tags matching `v*` (e.g., v1.0.0)
- Actions:
  - Create GitHub Release
  - Build tagged Docker images
  - Deploy to Azure production
  - Send notification

## Quick Start

### 1. Add Repository Secrets
See [CICD_SETUP.md](../CICD_SETUP.md) for detailed instructions.

### 2. Configure Branch Protection
In GitHub: Settings → Branches → Add protection rule for `main`

### 3. Test Workflow
```bash
git checkout -b test/ci
echo "test" >> README.md
git commit -am "test: ci/cd pipeline"
git push origin test/ci
# Create pull request and watch Actions tab
```

## Monitoring

View workflow runs:
- GitHub UI: Repository → Actions
- GitHub CLI: `gh run list`

Download logs:
```bash
gh run download <run-id>
```

## Making Changes

1. Edit workflow files in this directory
2. Test locally with `act`: `act push`
3. Commit: `git commit -m "ci: update workflow"`
4. The workflow itself validates the changes

## Documentation

- [CICD.md](../CICD.md) - Comprehensive CI/CD documentation
- [CICD_SETUP.md](../CICD_SETUP.md) - Setup and configuration guide
- [DOCKER_GUIDE.md](../DOCKER_GUIDE.md) - Docker building and publishing

## Status

All workflows are active:
- ✅ tests.yml - Active
- ✅ deploy.yml - Active (main only)
- ✅ pr-checks.yml - Active
- ✅ scheduled.yml - Active (daily)
- ✅ release.yml - Active (tags only)

## Support

For issues:
1. Check workflow logs in GitHub Actions
2. Review error messages
3. Test locally with `act`
4. Consult [CICD.md](../CICD.md)

## Related Files

- [.pylintrc](../.pylintrc) - Pylint configuration
- [.bandit](../.bandit) - Bandit security configuration
- [.pre-commit-config.yaml](../.pre-commit-config.yaml) - Pre-commit hooks
- [sonar-project.properties](../sonar-project.properties) - SonarQube configuration
