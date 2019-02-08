FROM python:3.7-alpine as builder

RUN apk --update add linux-headers g++ make
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

FROM python:3.7-alpine
# grpc dep
RUN apk add libstdc++

COPY --from=builder /usr/local/lib/python3.7 /usr/local/lib/python3.7
COPY ./code /opt/app
COPY requirements.txt requirements.txt

ENV HTTP_PORT 8080
ENV GRPC_PORT 50051
ENV METRICS_PORT 9100

ENV CONFIG /opt/config.json

ENTRYPOINT ["/opt/app/entrypoint.py"]