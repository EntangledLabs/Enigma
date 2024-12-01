# syntax=docker/dockerfile:1
FROM python:3.13-alpine
WORKDIR /enigma_engine
COPY ./requirements_enigma.txt /enigma_engine/requirements_enigma.txt
RUN python -m pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir --upgrade -r /enigma_engine/requirements_enigma.txt
COPY ./engine /enigma_engine/engine
COPY ./main.py /enigma_engine/main.py
COPY ./settings.toml /enigma_engine/settings.toml
EXPOSE 4731
CMD ["python", "main.py"]