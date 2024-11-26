# Enigma Scoring Engine with Parable Interactive Panel
A scoring engine for Red vs Blue cybersecurity competitions.

Built on Python 3.13.0 with Django and FastAPI

Highly extensible with a common framework for custom service checks

Uses NGINX as a reverse proxy and PostgreSQL for DB

The following table lists the ports of each service:

| Service | Port(s) |
|---|---|
|Enigma|4731|
|Parable|5070|
|PostgreSQL|8721|
|Nginx|80,443|

Nginx should be the only service exposed