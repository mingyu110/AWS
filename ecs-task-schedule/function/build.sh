#!/bin/bash

# Build the Docker image
docker build -t ecs-task-scheduler-build.

# Create a container from the image
container_id=$(docker create ecs-task-scheduler-build)

# Copy the contents of the container to a local directory
docker cp $container_id:/var/task ./package

# Clean up
docker rm $container_id

# Zip the contents of the local directory
cd package
zip -r ../ecs-task-scheduler.zip .
cd ..

# Clean up
rm -rf package