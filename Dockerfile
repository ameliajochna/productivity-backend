FROM python:3.11-slim-bullseye

RUN pip install poetry \
    && poetry config virtualenvs.create false

WORKDIR /productivity

COPY poetry.lock .
COPY pyproject.toml .

RUN apt-get update && apt-get install -y git
RUN poetry install --no-root --no-dev

COPY __init__.py .
COPY .pre-commit-config.yaml .
COPY database.py .
COPY gen_postgres_schema.sh .
COPY main.py .
COPY models.py .
COPY schemas.py .
COPY services.py .

EXPOSE 5432

CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
