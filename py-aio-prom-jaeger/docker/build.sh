#!/bin/bash
set -ex

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." >/dev/null && pwd )"
NAME=$(basename $DIR)
TAG=${TAG:-"latest"}

docker build -t $NAME:$TAG -f $DIR/docker/Dockerfile $DIR
docker build -t siege:4.0.4 -f $DIR/docker/Dockerfile-siege $DIR