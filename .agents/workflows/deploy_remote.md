---
description: Deploy the Website to Production via GitHub
---

# Remote GitHub Deployment

// turbo-all

> [!CAUTION]
> **Shell Safety:** PowerShell (v5.1) and Unix shells handle command chaining differently. To ensure reliability, **execute each step independently** as a separate command call.

1. Stage all local modifications:
```bash
git add .
```

2. Commit with a descriptive deployment tracking message:
```bash
git commit -m "chore: autonomous deployment push"
```

3. Route the changes upward to trigger the `deploy.yml` CI/CD pipeline:
```bash
git push
```
