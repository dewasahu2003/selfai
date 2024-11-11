FROM python:3.11-slim

RUN apt-get update --fix-missing && apt-get install -y \
    gcc \
    python3-dev \
    curl \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry
ENV PATH="etc/poetry/bin:$PATH"
WORKDIR /app
COPY ./pyproject.toml ./poetry.lock ./
RUN poetry install --no-root
COPY ./ ./
ENV PYTHONPATH=/app
CMD ["poetry","run","python","cdc.py","&&","tail","-f","/dev/null"]