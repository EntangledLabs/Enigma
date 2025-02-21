# syntax=docker/dockerfile:1
FROM python:3.13-alpine

WORKDIR /app

# Install requirements
COPY --from=ghcr.io/astral-sh/uv:0.5.31 /uv /uvx /bin/

COPY /requirements/parable.txt /app/requirements.txt
RUN uv pip install --system -r /app/requirements.txt

# Copy modules
COPY /parable /app/parable
COPY /enigma_models /app/enigma_models

# Copy main.py
COPY /main/parable/main.py /app/main.py

# Run main.py
CMD ["python", "main.py"]