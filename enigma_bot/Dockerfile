# syntax=docker/dockerfile:1
FROM python:3.13-alpine
WORKDIR /enigma_bot
COPY ./requirements_enigma_bot.txt /enigma_bot/requirements_enigma_bot.txt
COPY ./requirements_enigma_requests.txt /enigma_bot/requirements_enigma_requests.txt
RUN python -m pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir --upgrade -r /enigma_bot/requirements_enigma_bot.txt
RUN pip install --no-cache-dir --upgrade -r /enigma_bot/requirements_enigma_requests.txt
COPY ./bot /enigma_bot/bot
COPY ./enigma_requests /enigma_bot/enigma_requests
COPY ./main.py /enigma_bot/main.py
CMD ["python", "main.py"]