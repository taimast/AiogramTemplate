FROM ghcr.io/withlogicco/poetry:1.6.1
WORKDIR /app
COPY pyproject.toml ./
RUN poetry install --no-root --without dev
COPY crying crying
COPY README.md README.md
ENV PYTHONPATH=/app
