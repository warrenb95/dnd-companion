ARG PYTHON_VERSION=3.13-slim

FROM python:${PYTHON_VERSION}

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install LiteFS
RUN apt-get update && apt-get install -y \
    ca-certificates \
    curl \
    fuse3 \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

ADD https://github.com/superfly/litefs/releases/download/v0.5.11/litefs-v0.5.11-linux-amd64.tar.gz /tmp/litefs.tar.gz
RUN tar -C /usr/local/bin -xzf /tmp/litefs.tar.gz && rm /tmp/litefs.tar.gz

RUN mkdir -p /code /litefs /var/lib/litefs /litefs/media && \
    chmod 755 /litefs/media

WORKDIR /code

COPY requirements.txt /tmp/requirements.txt
RUN set -ex && \
    pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt && \
    rm -rf /root/.cache/

COPY . /code
COPY litefs.yml /etc/litefs.yml
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENV SECRET_KEY "BosFk8bX3pVT6b767AtE5IHnu30WVNdmDBgA2PMiUlP78gStTw"
RUN python manage.py collectstatic --noinput

EXPOSE 8080

CMD ["/entrypoint.sh", "litefs", "mount"]
