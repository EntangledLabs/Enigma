# syntax=docker/dockerfile:1
FROM nginx:stable-alpine
RUN rm /etc/nginx/conf.d/default.conf
COPY parable.conf /etc/nginx/conf.d/parable.conf