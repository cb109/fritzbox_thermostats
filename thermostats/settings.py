"""
Django settings for thermostats project.

Generated by 'django-admin startproject' using Django 3.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os

from decouple import Csv, config

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY", default="local-dev-super-secret-key")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DEBUG", default=False, cast=bool)

ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="127.0.0.1", cast=Csv())

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "thermostats.thermostats",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "thermostats.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "thermostats.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",},
]


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = config("TIME_ZONE", default="UTC", cast=str)

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = "/static/"

TIME_INPUT_FORMATS = [
    "%H:%M",
]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "colored": {
            "()": "colorlog.ColoredFormatter",
            "format": (
                "%(asctime)s %(log_color)s[%(levelname)s]"
                "%(reset)s%(bold_white)s %(name)s%(reset)s: "
                "%(message)s"
            ),
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "log_colors": {
                "DEBUG": "bold_cyan",
                "INFO": "bold_green",
                "WARNING": "bold_yellow",
                "ERROR": "bold_red",
                "CRITICAL": "bold_purple",
            },
        },
    },
    "handlers": {
        "colored_console": {"class": "logging.StreamHandler", "formatter": "colored"},
    },
    "loggers": {
        "thermostats": {
            "level": "DEBUG",
            "handlers": ["colored_console"],
            "propagate": True,
        },
    },
}

TEMPERATURE_OFF = config("TEMPERATURE_OFF", default=126.5, cast=float)
TEMPERATURE_FALLBACK = config("TEMPERATURE_FALLBACK", default=0, cast=float)

FRITZBOX_HOST = config("FRITZBOX_HOST", default="", cast=str)
FRITZBOX_USER = config("FRITZBOX_USER", default="", cast=str)
FRITZBOX_PASSWORD = config("FRITZBOX_PASSWORD", default="", cast=str)

PUSHOVER_USER_KEY = config("PUSHOVER_USER_KEY", default="", cast=str)
PUSHOVER_API_TOKEN = config("PUSHOVER_API_TOKEN", default="", cast=str)
