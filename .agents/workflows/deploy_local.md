---
description: Redeploy the Website Locally via Docker
---

# Redeploy Website via Docker

// turbo-all

> [!NOTE]
> **Cross-Platform Compatibility:** This workflow is atomic for maximum reliability on Windows (PowerShell/CMD), macOS, and Linux. Do not chain commands with `&&` or `;` as shell behavior varies across platforms.

1. Rebuild and restart the Docker container in detached mode:
```bash
docker-compose up --build -d
```

2. Verify the container is running:
```bash
docker-compose ps
```

The site will be available at http://localhost:8080 once the container is started.