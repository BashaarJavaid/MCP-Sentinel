FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*
RUN python -m pip install pipx==1.16.0
RUN pipx install portunusmcp-sentinel==1.2.1
ENV PATH="/root/.local/bin:${PATH}"
WORKDIR /work
