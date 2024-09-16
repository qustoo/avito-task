#!/bin/bash


# Build image
docker build -t my_fastapi_app .

# Run image
docker run -d  -p 8080:8080 --name fastapi_container my_fastapi_app