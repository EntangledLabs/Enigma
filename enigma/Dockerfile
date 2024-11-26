# syntax=docker/dockerfile:1
FROM python:3.13-alpine
WORKDIR /enigma_engine
COPY ./requirements.txt /enigma_engine/requirements.txt
RUN python -m pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir --upgrade -r /enigma_engine/requirements.txt
COPY ./enigma /enigma_engine/enigma
COPY ./main.py /enigma_engine/main.py
EXPOSE 4731
CMD ["python", "main.py"]