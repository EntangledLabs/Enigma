# syntax=docker/dockerfile:1
FROM python:3.13-alpine
WORKDIR /engine
COPY main.py .
COPY enigma/ enigma
COPY boxes/ boxes/
COPY creds/ creds/
COPY injects/ injects/
COPY logs/ logs/
COPY scores/ scores/
RUN --mount=type=bind,source=requirements.txt,target=/tmp/requirements.txt \
    pip install --requirement /tmp/requirements.txt
CMD ["python", "./main.py"]