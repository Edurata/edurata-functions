#!/bin/bash

# Define variables
VERSION="1.0.0"
IMAGE_TAG="edurata/clone-git"

# Push stage
docker login -u edurata -p $DOCKER_HUB_PW
echo "$VERSION is being built"
docker build -t $IMAGE_TAG:$VERSION -t $IMAGE_TAG:latest .
docker push $IMAGE_TAG:$VERSION
docker push $IMAGE_TAG:latest
