# {{ cookiecutter.project_name }}

## Overview

## Local Development Setup

All REVSYS projects going forward will use Python 3.6, Docker, and Docker Compose.

Make a Python 3.6.x virtualenv.

Copy env.template to .env and adjust values to match your local environment:

    cp env.template .env

Then run

    docker-compose up

This will create the Docker image, install dependencies, start the services defined in `docker-compose.yaml`, and start the webserver.

## Running the tests

To run the tests, execute:

    docker-compose run --rm web pytest

## Deploying

TDB

## Production Environment Considerations

TDB

