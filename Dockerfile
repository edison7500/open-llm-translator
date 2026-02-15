FROM python:3.11.10-slim-bullseye
ENV PYTHONUNBUFFERED 1

# The installer requires curl (and certificates) to download the release archive
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates

# Download the latest installer
ADD https://astral.sh/uv/install.sh /uv-installer.sh

# Run the installer then remove it
RUN sh /uv-installer.sh && rm /uv-installer.sh

# Ensure the installed binary is on the `PATH`
ENV PATH="/root/.local/bin/:$PATH"

COPY . /opt/open-llm-transaltor
WORKDIR /opt/open-llm-transaltor

RUN touch .env
# cleanup
RUN uv sync --locked

# add user
RUN useradd -s /sbin/nologin -u 1001 -d /opt/open-llm-transaltor transaltor

EXPOSE 8000
