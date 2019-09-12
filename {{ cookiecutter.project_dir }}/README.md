# {{ cookiecutter.project_name }}

## Overview

[Project description]

## Local Development Setup

All Avocado projects going forward will use Python 3.7, Docker, and Docker Compose.

Make a Python 3.7.x virtualenv.

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

### Health Checks

Health checks can be viewed at `/health` in a browser or as JSON if you use
`curl -H "Accept: application/json" http://localhost:8000/health/`

Currently includes checks for:

- database


## Environment Variables

### ROLLBAR_ACCESS_TOKEN

This is the access token for a specific project on rollbar.com. In order to
get this token, visit https://rollbar.com/emoneyadvisor/<project-name>/settings/access_tokens/
where `<project_name>` is the name of the rollbar project that you wish to
send messages to. The token that you should use is called `post_server_item`.

### ROLLBAR_ENVIRONMENT

This environment variables allows us to tag messages by deployment for filtering.
We can create any number of environment names, but common ones are "development",
"staging", and "production". This environment variable defaults to "development".

More on rollbar environments [here](https://docs.rollbar.com/docs/environments)
