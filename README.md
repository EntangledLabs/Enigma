# Enigma Scoring Engine with Parable Interactive Web Panel
A scoring engine for Red vs Blue cybersecurity competitions.

## Summary
Enigma is an all-in-one scoring engine for Red vs Blue (RvB) cybersecurity competitions. Enigma comes with Parable, a web interface purpose built for ease of use and a rich feature set.

Enigma is designed to be highly configurable and extensible. Custom score checks are Python classes that are automatically integrated and used.

Parable allows a competitor end user to view a wide variety of information relevant to their performance. In addition, Parable includes a comprehensive administration panel with the capability to modify almost every aspect of Enigma.

Future feature! Enigma will have Discord integration and will automatically manage channels and roles. Competitors will be able to submit various requests through Discord to supplement their use of Parable.

## Details
Built on Python 3.13.0 with Django and FastAPI

Highly extensible with a common framework for custom service checks

Uses NGINX as a reverse proxy and PostgreSQL for DB

The following table lists the ports of each service:

| Service | Port(s) |
|---|---|
|Enigma|4731|
|Parable|5070|
|PostgreSQL|8721/3141|
|Nginx|80,443|

Nginx should be the only service exposed