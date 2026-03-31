---
description: Redeploy the Website Locally via Docker
---

# Redeploy Website via Docker

// turbo-all

1. Rebuild and restart the Docker container in detached mode:
```
docker-compose up --build -d
```

2. Verify the container is running:
```
docker-compose ps
```

The site will be available at http://localhost:8080 once the container is started.