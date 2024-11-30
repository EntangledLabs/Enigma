# syntax=docker/dockerfile:1
FROM python:3.13-alpine
WORKDIR /enigma_bot
COPY ./requirements.txt /enigma_engine/requirements.txt
RUN python -m pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir --upgrade -r /enigma_engine/requirements.txt
COPY ./bot /enigma_bot/bot
COPY ./main.py /enigma_bot/main.py
CMD ["python", "main.py"]