import os

# If not using Celery, delete celery.py
celery = {{ cookiecutter.celery }}


def remove_celery_files():
    """ Remove celery.py """
    os.remove("config/celery.py")


def main():
    if {{ cookiecutter.celery }} is False:
        remove_celery_files()


if __name__ == "__main__":
    main()
