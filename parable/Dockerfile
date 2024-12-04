# syntax=docker/dockerfile:1
FROM python:3.13-alpine
WORKDIR /parable
COPY ./requirements_parable.txt /parable/requirements_parable.txt
COPY ./requirements_enigma_requests.txt /parabe/requirements_enigma_requests.txt
RUN python -m pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir --upgrade -r /parable/requirements_parable.txt
RUN pip install --no-cache-dir --upgrade -r /parable/requirements_parable.txt
RUN apk add curl
COPY ./parable /parable/parable
COPY ./frontend /parable/frontend
COPY ./enigma_requests /parable/enigma_requests
COPY ./manage.py /parable/manage.py
EXPOSE 5070
CMD ["gunicorn", "--workers=2", "--bind=0.0.0.0:5070", "frontend.wsgi"]