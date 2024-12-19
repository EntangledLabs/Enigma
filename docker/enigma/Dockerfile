# syntax=docker/dockerfile:1
FROM python:3.13-alpine

WORKDIR /app

# Install requirements
COPY /enigma/requirements.txt /app/requirements.txt

RUN python -m pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# Copy modules
COPY /enigma /app/enigma
COPY /db_models /app/db_models

# Copy main.py
COPY /main/enigma/main.py /app/main.py

# Run main.py
CMD ["python", "main.py", "--reset"]