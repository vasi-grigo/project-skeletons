FROM python:3.7-alpine as builder

RUN \
    apk --update add linux-headers g++ make \
    && pip install aiohttp aioprometheus psutil uvloop


FROM python:3.7-alpine

COPY --from=builder /usr/local/lib/python3.7 /usr/local/lib/python3.7
COPY ./code app

WORKDIR /app

ENV REST_PORT 8080
ENV METRICS_PORT 9100
# ENV CONFIG ./config.json.dist

ENTRYPOINT ["./entrypoint.py"]