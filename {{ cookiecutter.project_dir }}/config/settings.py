import logging
import os
import sys

import envparse

from avo.core.structlogging.configure import django_configure as log_django_configure

env = envparse.Env()

READ_DOT_ENV_FILE = env.bool("DJANGO_READ_DOT_ENV_FILE", default=False)
if READ_DOT_ENV_FILE:
    env.read_envfile()
    print("The .env file has been loaded. See settings.py for more information")

# Name of our service
SERVICE_NAME = "{{ cookiecutter.project_name }}"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DJANGO_DEBUG", cast=bool, default=False)

# Whether to log to a local ElasticSearch or not
LOCAL_LOGGING = env("LOCAL_LOGGING", cast=bool, default=False)

# Determine if we're in testing or not.
TESTING = env("TESTING", cast=bool, default=False)

if DEBUG:
    lh = logging.StreamHandler(sys.stderr)
    envparse.logger.addHandler(lh)
    envparse.logger.setLevel(logging.DEBUG)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = BASE_DIR
APPS_DIR = os.path.join(ROOT_DIR, "config")


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")


host_list = env("ALLOWED_HOSTS", default="localhost").split(",")
ALLOWED_HOSTS = [el.strip() for el in host_list]


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

# Third-party apps
INSTALLED_APPS += [
    "rest_framework",
    "rest_framework_swagger",
    "django_extensions",
    "health_check",
    "health_check.db",
    {%- if cookiecutter.redis == 'True' %}"health_check.cache",{% endif -%}
    {%- if cookiecutter.celery == 'True' %}"health_check.contrib.celery",{% endif -%}
]

# Our Apps
INSTALLED_APPS += []

MIDDLEWARE = [
    "tracer.middleware.RequestID",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

if DEBUG:
    # These are necessary to turn on Whitenoise which will serve our static
    # files while doing local development
    MIDDLEWARE.append("whitenoise.middleware.WhiteNoiseMiddleware")
    WHITENOISE_USE_FINDERS = True
    WHITENOISE_AUTOREFRESH = True

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django_db_geventpool.backends.postgresql_psycopg2",
        "HOST": env("PGHOST"),
        "NAME": env("PGDATABASE"),
        "PASSWORD": env("PGPASSWORD"),
        "PORT": int(env("PGPORT", default=5432)),
        "USER": env("PGUSER"),
        "CONN_MAX_AGE": 0,
        "OPTIONS": {"MAX_CONNS": 200},
    }
}

# Password validation
# Only used in production
AUTH_PASSWORD_VALIDATORS = []

# Sessions

# Give each project their own session cookie name to avoid local development
# login conflicts
SESSION_COOKIE_NAME = "config-sessionid"

# Increase default cookie age from 2 to 12 weeks
SESSION_COOKIE_AGE = 60 * 60 * 24 * 7 * 12

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = env("STATIC_URL", default="/static/")
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

# Swagger Settings
SWAGGER_SETTINGS = {"SECURITY_DEFINITIONS": {}}

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# Testing values
if TESTING:
    PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]


# Logging setup
# Configure struct log
LOGGING = log_django_configure(SERVICE_NAME, BASE_DIR, env)

{% if cookiecutter.redis == "True" %}REDIS_HOST = env("REDIS_HOST", default="redis"){% endif %}

{% if cookiecutter.redis == "True" %}
# Cache
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{REDIS_HOST}:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient"
        },
    }
}
{% endif %}

{%- if cookiecutter.celery == "True" %}
# Configure Celery
CELERY_BROKER_URL = f"redis://{REDIS_HOST}:6379/1"
CELERY_RESULT_BACKEND = f"redis://{REDIS_HOST}:6379/1"
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "America/Los_Angeles"
{% endif -%}
