#!/bin/bash
set -ex

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." >/dev/null && pwd )"
NAME=$(basename $DIR)
TAG=${TAG:-"latest"}

# regenerate protobuff files and copy over
docker build -t $NAME-protoc:latest -f $DIR/docker/Dockerfile-protoc $DIR
id=$(docker run -dit $NAME-protoc:latest sh)
docker cp $id:/opt/app/pyskull_grpc.py $DIR/code
docker cp $id:/opt/app/pyskull_pb2.py $DIR/code
docker stop $id
docker rm $id

# build the actual image
docker build -t $NAME:$TAG -f $DIR/docker/Dockerfile $DIR