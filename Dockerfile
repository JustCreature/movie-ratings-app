FROM python:3.12-slim

ARG INSTALL_DEV=false

COPY ./pyproject.toml ./poetry.lock* /code/

WORKDIR /code/

ENV POETRY_VERSION=2.1.3
RUN pip install --upgrade pip setuptools && pip install --no-cache-dir "poetry==$POETRY_VERSION"
RUN apt-get update && apt-get install libpq-dev -y && apt-get clean && poetry config virtualenvs.create false && \
    poetry install $(test "$INSTALL_DEV" = "false" && echo "--no-dev") --no-root --no-interaction --no-ansi

COPY ./Makefile /code/

COPY ./src /code

ENV PYTHONPATH=/code

CMD [ "poetry", "run", "python", "-m", "app.main"]
