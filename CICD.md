# CI/CD Pipeline Documentation

## Overview

This project uses **GitHub Actions** for continuous integration and continuous deployment (CI/CD), ensuring code quality, automated testing, security scanning, and deployment to Azure.

---

## Workflow Files

### 1. **tests.yml** - Tests & Build
**Triggers**: Push to `main`/`develop`, Pull Requests

**Jobs**:
- **Test** (Python 3.9, 3.10, 3.11)
  - Run pytest with coverage
  - Code linting with pylint
  - Code formatting check with black
  - Upload coverage to Codecov
  
- **Build & Push Docker**
  - Build backend Docker image
  - Build frontend Docker image
  - Push to GitHub Container Registry (GHCR)
  
- **Security Scanning**
  - Trivy vulnerability scanner
  - Bandit security check
  
- **Code Quality Analysis**
  - Flake8 style checking
  - SonarQube scanning (optional)
  
- **Dependency Security Check**
  - Safety check for known vulnerabilities
  - pip-audit for dependency scanning

### 2. **deploy.yml** - Deploy to Azure
**Triggers**: Push to `main`, Workflow dispatch (manual)

**Jobs**:
- **Build** - Build and push Docker images to GHCR
- **Deploy** - Deploy containers to Azure Container Instances
- **Notify** - Create GitHub Deployment record

### 3. **pr-checks.yml** - PR Quality Gates
**Triggers**: Pull requests, Push to main/develop

**Jobs**:
- **PR Validation** - Check PR title format and description
- **Commit Lint** - Validate conventional commit messages
- **Format Check** - Black, isort, pylint checks
- **Type Checking** - mypy static type analysis
- **Deps Check** - Security vulnerability scanning
- **Docs Check** - Documentation presence validation
- **Coverage Check** - Minimum 70% test coverage required
- **File Size Check** - Warn about large files

### 4. **scheduled.yml** - Nightly Maintenance
**Triggers**: Daily at 2 AM UTC, Manual dispatch

**Jobs**:
- **Update Dependencies** - Auto-create PR for dependency updates
- **Nightly Tests** - Run full test suite on all Python versions
- **Security Scan** - Nightly vulnerability scanning
- **Nightly Build** - Build Docker images for cache
- **Performance Test** - Run performance benchmarks
- **Quality Check** - Generate code quality metrics

### 5. **release.yml** - Release Management
**Triggers**: Git tags matching `v*` pattern

**Jobs**:
- **Create Release** - Generate GitHub release notes
- **Build Release** - Build and tag release Docker images
- **Deploy Release** - Deploy to production Azure instance
- **Notify Release** - Send release notification

---

## Setup Instructions

### 1. GitHub Repository Secrets

Add these secrets to your GitHub repository (Settings → Secrets and variables → Actions):

```
AZURE_CREDENTIALS          # Azure service principal credentials (JSON)
AZURE_RESOURCE_GROUP       # Azure resource group name
OPENAI_API_KEY            # OpenAI API key
SUPABASE_URL              # Supabase project URL
SUPABASE_KEY              # Supabase service role key
JWT_SECRET_KEY            # Strong secret key for JWT
SMTP_USER                 # Email SMTP username
SMTP_PASSWORD             # Email SMTP password
EMAIL_FROM                # Email from address
SONAR_TOKEN              # SonarQube token (optional)
```

### 2. Azure Credentials Setup

Create service principal with Docker push permissions:

```bash
# Login to Azure
az login

# Create service principal
az ad sp create-for-rbac \
  --name rag-service-cicd \
  --role contributor \
  --scopes /subscriptions/{subscription-id}

# Copy the JSON output and add as AZURE_CREDENTIALS secret
```

### 3. GitHub Container Registry Setup

Ensure you have authentication:

```bash
# Create personal access token with 'packages' scope
# Use in GITHUB_TOKEN (automatically provided by GitHub Actions)
```

### 4. Enable Required Features

In repository settings:
- ✅ Enable Actions
- ✅ Allow public actions (if workflow uses public actions)
- ✅ Enable security features (Dependabot, code scanning)

---

## Workflow Triggers

### Automatic Triggers

| Workflow | Trigger | Branches |
|----------|---------|----------|
| tests.yml | Push, PR | main, develop |
| pr-checks.yml | PR, Push | main, develop |
| scheduled.yml | Cron (2 AM UTC) | - |
| deploy.yml | Push to main | main |
| release.yml | Git tag `v*` | - |

### Manual Triggers

All workflows support `workflow_dispatch` for manual triggering:

```bash
# Via GitHub CLI
gh workflow run deploy.yml

# Via GitHub UI
Settings → Actions → Select workflow → Run workflow
```

---

## Environment Variables

### In Workflows

All environment variables from `.env` are passed to jobs as secrets:

```yaml
env:
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
  # ... etc
```

### Container Environment

Docker containers receive environment variables:

```yaml
environment-variables:
  OPENAI_API_KEY=${{ secrets.OPENAI_API_KEY }}
  SUPABASE_URL=${{ secrets.SUPABASE_URL }}
```

---

## Status Checks & Required Checks

### Setting Required Status Checks

In GitHub repository settings (Settings → Branches → Branch protection):

Enable required status checks for `main`:
- ✅ test (Python 3.11) - All test jobs
- ✅ security - Trivy scan
- ✅ quality - Code quality analysis
- ✅ build - Docker build
- ✅ pr-checks - PR validation (for PRs)

---

## Monitoring & Logs

### View Workflow Runs

```bash
# Via GitHub CLI
gh run list
gh run view <run-id>
gh run view <run-id> --log

# Via GitHub UI
Repository → Actions → Select workflow → View runs
```

### View Job Logs

```bash
# Download logs
gh run download <run-id>

# View specific job
gh run view <run-id> --job <job-id>
```

---

## Testing Locally

Simulate GitHub Actions locally with `act`:

```bash
# Install act
brew install act  # macOS
# or download from https://github.com/nektos/act

# Run workflow locally
act push  # Simulates push event
act pull_request  # Simulates PR
```

---

## Troubleshooting

### Common Issues

#### "Docker image push failed"
```
Solution: Check GITHUB_TOKEN secret and container registry permissions
```

#### "Tests failed in CI but pass locally"
```
Solution: 
1. Check Python version differences
2. Verify environment variables are set
3. Check for platform-specific issues (Windows vs Linux)
```

#### "Azure deployment failed"
```
Solution:
1. Verify AZURE_CREDENTIALS secret is valid
2. Check Azure resource group exists
3. Verify resource limits aren't exceeded
4. Check Azure quota/billing
```

#### "Security scan reporting false positives"
```
Solution:
1. Review Trivy alerts
2. Add exceptions in .github/workflows/
3. Update security policy if needed
```

---

## Customization

### Add Custom Steps

Edit workflow files in `.github/workflows/` and add steps:

```yaml
- name: Custom step
  run: |
    echo "Custom command here"
    python your_script.py
```

### Modify Triggers

Change `on` section:

```yaml
on:
  push:
    branches: [main, production]  # Add branches
  schedule:
    - cron: '0 12 * * *'  # Change schedule
```

### Add Notifications

Add steps to notify on failure:

```yaml
- name: Notify Slack
  if: failure()
  uses: slackapi/slack-github-action@v1
  with:
    webhook-url: ${{ secrets.SLACK_WEBHOOK }}
```

### Matrix Builds

Current matrix for Python versions:

```yaml
strategy:
  matrix:
    python-version: ['3.9', '3.10', '3.11']
```

---

## Best Practices

✅ **Do**:
- Use branch protection rules
- Require status checks before merge
- Review workflow logs regularly
- Keep secrets secure and rotated
- Use semantic versioning for releases
- Add required reviewers for PRs
- Document deployment procedures

❌ **Don't**:
- Commit secrets to repository
- Use workflow_dispatch for production deployments
- Skip security scanning
- Ignore test failures
- Use overly broad permissions
- Test in production directly

---

## Performance Tips

### Reduce Workflow Duration

1. **Cache Dependencies**
   ```yaml
   - uses: actions/setup-python@v4
     with:
       cache: 'pip'
   ```

2. **Use Conditional Steps**
   ```yaml
   if: github.event_name == 'push' && github.ref == 'refs/heads/main'
   ```

3. **Parallelize Jobs**
   ```yaml
   job-name:
     needs: [job1, job2]  # Run after multiple jobs
   ```

4. **Use Smaller Base Images**
   - Use `python:3.11-slim` instead of `python:3.11`

---

## Maintenance

### Regular Checks

- [ ] Review workflow status monthly
- [ ] Update action versions quarterly
- [ ] Rotate secrets annually
- [ ] Clean up old artifacts
- [ ] Review security scanning results

### Clean Up

```bash
# Remove old artifacts (> 30 days)
gh run list --status completed --limit 100 | \
  awk '{print $1}' | \
  xargs -I {} gh run delete {}
```

---

## Next Steps

1. ✅ Add all required secrets to GitHub
2. ✅ Configure branch protection rules
3. ✅ Test workflows manually (make a PR)
4. ✅ Monitor first few production deployments
5. ✅ Adjust thresholds based on feedback

---

## Support

For issues or questions:
- Check GitHub Actions documentation: https://docs.github.com/en/actions
- Review workflow logs in GitHub UI
- Test locally with `act`
- Enable debug logging in workflows

---

## Related Documentation

- [Docker Guide](./DOCKER_GUIDE.md)
- [Azure Deployment](./AZURE_DEPLOYMENT.md)
- [Local Development](./README.md)
- [Testing Guide](./TESTING.md)
