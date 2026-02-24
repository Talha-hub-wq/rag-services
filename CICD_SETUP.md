# CI/CD Setup Guide

## Quick Setup for GitHub Actions

### Step 1: Add Secrets to GitHub

Go to your repository: **Settings → Secrets and variables → Actions**

Click **"New repository secret"** and add:

```
1. AZURE_CREDENTIALS
   Type: JSON (from Azure service principal)
   
2. AZURE_RESOURCE_GROUP
   Type: Text
   Value: your-resource-group-name

3. OPENAI_API_KEY
   Type: Text
   Value: sk-...

4. SUPABASE_URL
   Type: Text
   Value: https://...supabase.co

5. SUPABASE_KEY
   Type: Text
   Value: eyJ...

6. JWT_SECRET_KEY
   Type: Text
   Value: your-very-strong-secret-key-min-32-chars

7. SMTP_USER
   Type: Text
   Value: your-email@gmail.com

8. SMTP_PASSWORD
   Type: Text
   Value: your-app-password

9. EMAIL_FROM
   Type: Text
   Value: your-email@gmail.com
```

### Step 2: Configure Branch Protection

**Settings → Branches → Add rule** for `main` branch:

```
✅ Require a pull request before merging
✅ Require status checks to pass
   - Select: build (Python 3.11)
   - Select: security
   - Select: quality
✅ Require code reviews: 1
✅ Require approval of reviews
```

### Step 3: Get Azure Credentials

Run these commands:

```bash
# Login to Azure
az login

# Set your subscription
az account set --subscription "YOUR-SUBSCRIPTION-ID"

# Create service principal
az ad sp create-for-rbac \
  --name rag-service-cicd-sp \
  --role contributor \
  --scopes /subscriptions/YOUR-SUBSCRIPTION-ID

# Output will be:
# {
#   "appId": "...",
#   "displayName": "rag-service-cicd-sp",
#   "password": "...",
#   "tenant": "..."
# }

# Copy entire JSON as AZURE_CREDENTIALS secret
```

### Step 4: Verify Setup

Push a test commit:

```bash
git add .
git commit -m "test: ci/cd pipeline verification"
git push origin main
```

Check **Actions** tab → Your workflow should run automatically

---

## Local Development with Pre-commit

### Install Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Install the git hooks
pre-commit install

# (Optional) Run on all files
pre-commit run --all-files
```

This will automatically run checks before each commit.

---

## Workflows Explained

### 1. **tests.yml** (Every Push & PR)

```
Triggers: Push to main/develop, Pull Requests
Takes: ~15-20 minutes

Steps:
1. Test on Python 3.9, 3.10, 3.11 (in parallel)
   → pytest with coverage
   → pylint linting
   → black formatting
   
2. Build Docker images
   → Backend image → ghcr.io/owner/repo-backend:main
   → Frontend image → ghcr.io/owner/repo-frontend:main
   
3. Security scanning
   → Trivy for vulnerabilities
   → Bandit for security issues
   
4. Code quality
   → Flake8 style checks
   → Optional: SonarQube

5. Dependency checks
   → Safety for known vulnerabilities
   → pip-audit for updates
```

### 2. **deploy.yml** (Push to main only)

```
Triggers: Push to main branch
Takes: ~10-15 minutes
Requires: tests.yml success

Steps:
1. Build and push images to GHCR
   
2. Deploy to Azure
   → Backend Container Instance
   → Frontend Container Instance
   
3. Create GitHub Deployment record
```

### 3. **pr-checks.yml** (PRs & Pushes)

```
Triggers: Pull requests, Push to main/develop
Takes: ~5-10 minutes

Validates:
- PR title format (conventional commits)
- PR description exists
- Code formatting (black, isort, pylint)
- Type checking (mypy)
- Test coverage minimum (70%)
- Dependency vulnerabilities
- Documentation presence
- File sizes
```

### 4. **scheduled.yml** (Daily 2 AM UTC)

```
Triggers: Cron schedule (daily)
Takes: ~20-30 minutes

Jobs:
- Auto-update dependencies (creates PR)
- Run full test suite on all Python versions
- Nightly security scan
- Build Docker images (caching)
- Performance benchmarks
- Code quality metrics
```

### 5. **release.yml** (Git tags v*)

```
Triggers: Push git tag 'v*' (e.g., v1.0.0)
Takes: ~15-20 minutes

Steps:
1. Create GitHub Release
2. Build release images (tagged with version)
3. Deploy to Azure production
4. Send notification
```

---

## Monitoring Workflows

### View Status

```bash
# GitHub CLI
gh run list                    # List recent runs
gh run view <run-id>          # View run details
gh run view <run-id> --log    # Download logs

# Or use GitHub UI
Repository → Actions → Select workflow → Select run
```

### Troubleshooting

**Workflow failed? Check logs:**

1. Go to Actions tab
2. Click failed workflow run
3. Click failed job
4. Scroll to see error details

**Common errors:**

| Error | Solution |
|-------|----------|
| "Resource not found" | Check Azure credentials secret |
| "Docker push failed" | Verify GITHUB_TOKEN permissions |
| "Tests failed" | Run tests locally with `pytest` |
| "Linting errors" | Run `black . && isort .` locally |

---

## Making Changes to Workflows

### Edit Workflow Files

```bash
# Files are in .github/workflows/
.github/workflows/
├── tests.yml           # Run tests & build
├── deploy.yml          # Deploy to Azure
├── pr-checks.yml       # PR validation
├── scheduled.yml       # Daily maintenance
└── release.yml         # Release management
```

### Test Workflow Locally

```bash
# Install act (local GitHub Actions runner)
brew install act  # macOS

# Run workflow locally
act -l                    # List workflows
act push                  # Simulate push
act pull_request          # Simulate PR
```

---

## Security Best Practices

✅ **Do:**
- Rotate secrets monthly
- Use service principals with minimal permissions
- Review workflow logs regularly
- Keep actions updated
- Use branch protection rules
- Enable security features in GitHub

❌ **Don't:**
- Commit secrets to repo
- Use personal access tokens in workflows
- Skip security scanning
- Disable required checks
- Use overly broad permissions

---

## Performance Optimization

### Reduce Build Time

1. **Cache Python dependencies:**
   ```yaml
   - uses: actions/setup-python@v4
     with:
       python-version: "3.11"
       cache: 'pip'
   ```

2. **Use Docker layer caching:**
   ```yaml
   cache-from: type=registry,ref=ghcr.io/owner/repo:buildcache
   cache-to: type=registry,ref=ghcr.io/owner/repo:buildcache
   ```

3. **Run relevant tests only:**
   ```bash
   pytest tests/test_api.py -k "not slow"
   ```

4. **Parallelize matrix jobs:**
   ```yaml
   strategy:
     matrix:
       python-version: ['3.9', '3.10', '3.11']
   ```

---

## Next Steps

1. ✅ Add all secrets to GitHub
2. ✅ Configure branch protection
3. ✅ Create first PR to test workflows
4. ✅ Monitor first few deployments
5. ✅ Set up Slack notifications (optional)

---

## Support Resources

- GitHub Actions: https://docs.github.com/en/actions
- Azure Container Instances: https://docs.microsoft.com/en-us/azure/container-instances
- Docker Hub: https://hub.docker.com
- Pre-commit: https://pre-commit.com

---

## Checklist

Before going live:

- [ ] All secrets added to GitHub
- [ ] Branch protection rules configured
- [ ] Azure credentials verified
- [ ] Local testing passed
- [ ] First PR workflow completed successfully
- [ ] Deployment to Azure successful
- [ ] Team has access to monitoring tools
- [ ] Runbook created for manual interventions
- [ ] On-call procedures documented
- [ ] Rollback procedure tested
