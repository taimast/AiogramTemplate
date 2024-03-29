FROM ghcr.io/withlogicco/poetry:1.7.0-python-3.12
WORKDIR /app
COPY pyproject.toml ./
RUN poetry install --no-root --without dev
COPY src src
COPY alembic alembic
COPY alembic.ini alembic.ini
COPY README.md README.md
ENV PYTHONPATH=/app
