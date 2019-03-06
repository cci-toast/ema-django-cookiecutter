import envparse
import os
import sys
import logging
import logging.handlers

import structlog

from pythonjsonlogger import jsonlogger

env = envparse.Env()

READ_DOT_ENV_FILE = env.bool("DJANGO_READ_DOT_ENV_FILE", default=False)
if READ_DOT_ENV_FILE:
    env.read_envfile()
    print("The .env file has been loaded. See base.py for more information")

# Name of our service
SERVICE_NAME = "{{ cookiecutter.project_name }}"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DJANGO_DEBUG", cast=bool, default=False)

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
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

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
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = "/static/"
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

# Swagger Settings
SWAGGER_SETTINGS = {"SECURITY_DEFINITIONS": {}}

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# Testing values
if TESTING:
    PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]


# Logging setup
# Configure struct log
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.stdlib.render_to_log_kwargs,
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

# Configure Python logging
root = logging.getLogger()
root.setLevel(logging.INFO)


handler = logging.FileHandler("./python.log")
handler.setFormatter(jsonlogger.JsonFormatter())

root.addHandler(handler)

{% if cookiecutter.redis == "True" %}REDIS_HOST = env("REDIS_HOST", default="redis"){% endif %}

{%- if cookiecutter.celery == "True" %}
# Configure Celery
CELERY_BROKER_URL = f"redis://{REDIS_HOST}:6379"
CELERY_RESULT_BACKEND = f"redis://{REDIS_HOST}:6379"
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "America/Los_Angeles"
{% endif -%}
