FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*
RUN python -m pip install pipx==1.16.0
COPY portunusmc*.whl /dist/
RUN pipx install /dist/portunusmcp_sentinel-1.2.1-py3-none-any.whl
ENV PATH="/root/.local/bin:${PATH}"
WORKDIR /work
