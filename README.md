# REVSYS Django Cookiecutter Template / updated for Drexel Projects

Our own customized to our liking Django project layout.

**IMPORTANT**

- updated by removing references to rollbar and other internal repo.
- May have issues when run in production mode. Check logging setup

## Getting setup

First off you need [cookiecutter](https://github.com/audreyr/cookiecutter) installed:

```shell
pip install cookiecutter
```

Then all you need to do is run:

```shell
cookiecutter git@github.com:emoneyadvisor/django-cookiecutter.git
```

You will be prompted for questions and the project will be created in the
current directory.

## Core Settings Defaults

| name            | default | notes                                                                     |
| --------------- | ------- | ------------------------------------------------------------------------- |
| `ALLOWED_HOSTS` | []      |                                                                           |
| `DATABASE_URL`  |         | Defaults to `sqlite3`, but we may want to update to default to `postgres` |
| `DEBUG`         | `False` |                                                                           |
| `SECRET_KEY`    |         |                                                                           |

## Optional Settings Defaults, based on the project needs

| name                       | default | notes |
| -------------------------- | ------- | ----- |
| `REDIS_URL`                |         |       |
| `CELERY_BROKER_URL`        |         |       |
| `CELERY_RESULT_BACKEND`    |         |       |
| `CELERY_TASK_ALWAYS_EAGER` | `False` |       |
