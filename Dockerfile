# Stage 1: Build the static site
FROM python:3.12-slim AS builder

WORKDIR /app
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Explicitly copy execution and website content
COPY execution/ execution/
COPY website/ website/

# Build the site statically
RUN python execution/build_site.py

# Stage 2: Development / Test (Matches legacy behavior for docker-compose)
FROM python:3.12-slim AS dev

WORKDIR /app
ENV PYTHONUNBUFFERED=1

# Non-root user
RUN groupadd -g 1000 appgroup && \
    useradd -u 1000 -g appgroup -s /bin/sh -m appuser

# Copy over python packages and source
COPY --from=builder /usr/local /usr/local
COPY requirements.txt .
COPY execution/ execution/
COPY website/ website/

RUN chown -R appuser:appgroup /app
USER appuser
EXPOSE 8080

CMD ["sh", "-c", "python execution/build_site.py && python -m http.server 8080 -d website/public"]

# Stage 3: Production (Optimized Nginx deployment)
FROM nginx:alpine AS prod

# Expose standard HTTP port
EXPOSE 80

# Serve static files built in the builder stage
COPY --from=builder /app/website/public /usr/share/nginx/html

CMD ["nginx", "-g", "daemon off;"]
