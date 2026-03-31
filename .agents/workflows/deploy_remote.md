---
description: Deploy the Website to Production via GitHub
---

# Remote GitHub Deployment

// turbo-all

1. Stage all local modifications:
```bash
git add .
```

2. Commit with a generic deployment tracking message:
```bash
git commit -m "chore: autonomous deployment push"
```

3. Route the changes upward to trigger the `deploy.yml` CI/CD pipeline and execute the formal SSG builds and CSP Verification checks on the remote server:
```bash
git push
```
