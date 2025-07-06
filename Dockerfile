ARG PYTHON_VERSION=3.13-slim

FROM python:${PYTHON_VERSION}

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ca-certificates \
    fuse3 \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Install LiteFS
COPY --from=flyio/litefs:0.5 /usr/local/bin/litefs /usr/local/bin/litefs

# Create application directory
RUN mkdir -p /code

WORKDIR /code

# Install Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN set -ex && \
    pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt && \
    rm -rf /root/.cache/

# Copy application code
COPY . /code

# Copy LiteFS configuration
COPY litefs.yml /etc/litefs.yml

# Create entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Create directories for LiteFS
RUN mkdir -p /var/lib/litefs /litefs

# Set environment variables for LiteFS
ENV LITEFS_DIR="/litefs"

# Expose ports
EXPOSE 8000 8080

# Use entrypoint script
ENTRYPOINT ["/entrypoint.sh"]
CMD ["litefs", "mount"]
