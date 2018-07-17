import sys

# Ensure if celery is True that redis is True
celery = {{ cookiecutter.celery }}
redis = {{ cookiecutter.redis }}

if celery is True and redis is False:
    print("ERROR: Celery cannot be enabled without Redis")
    sys.exit(-1)
