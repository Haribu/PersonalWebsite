FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Ensure standard output is unbuffered
ENV PYTHONUNBUFFERED=1

# Create a non-root user and group
RUN groupadd -g 1000 appgroup && \
    useradd -u 1000 -g appgroup -s /bin/sh -m appuser

# Install system dependencies if any are needed (none for our pure python, but good practice)
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     && rm -rf /var/lib/apt/lists/*

# Copy python dependencies and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY website/ website/

# Ensure the non-root user owns the directories where files will be created
RUN chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Expose the standard port the python web server will use
EXPOSE 8080

# The default command builds the site and serves it
CMD ["sh", "-c", "python execution/build_site.py && python -m http.server 8080 -d website/public"]
