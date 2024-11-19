"""
Django settings for website project.

Generated by 'django-admin startproject' using Django 5.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from django.urls import reverse_lazy

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure--tj#@x^aa%5f_dfu56dfxmi87@_9md5+8a0bbt70^!c^5m@adz"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "a7d2-37-213-170-123.ngrok-free.app",
]

CSRF_TRUSTED_ORIGINS = ["https://a7d2-37-213-170-123.ngrok-free.app"]

INTERNAL_IPS = [
    "127.0.0.1",
]

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
    }
}

# Application definition

INSTALLED_APPS = [
    # Standard apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # other lib
    "rest_framework",
    "debug_toolbar",
    "drf_spectacular",
    "django_celery_results",
    "django_extensions",
    # Django apps
    "account.apps.AccountConfig",
    "cart.apps.CartConfig",
    "catalog.apps.CatalogConfig",
    "core.apps.CoreConfig",
    "order.apps.OrderConfig",
    "comparison.apps.ComparisonConfig",
    "discount.apps.DiscountConfig",
    "payment.apps.PaymentConfig",
    # DRF API
    "review.apps.ReviewConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

ROOT_URLCONF = "website.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "static"), os.path.join(BASE_DIR, 'templates')],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                # "account.context_processors.user_is_auth",
            ],
        },
    },
]

WSGI_APPLICATION = "website.wsgi.application"

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "ru"

TIME_ZONE = "Europe/Moscow"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "/static/"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "/media/"

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "auth.CustomUser"

LOGIN_URL = reverse_lazy("account:login")
LOGOUT_URL = reverse_lazy("account:logout")
LOGIN_REDIRECT_URL = reverse_lazy("core:index")
LOGOUT_REDIRECT_URL = reverse_lazy("core:index")

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = str(os.getenv("EMAIL_USER"))
EMAIL_HOST_PASSWORD = str(os.getenv("EMAIL_PASSWORD"))

# Session settings
SESSION_ENGINE = "django.contrib.sessions.backends.db"
# Время жизни сессии (2 недели)
SESSION_COOKIE_AGE = 1209600
# Обновляем таймер каждый заход пользователя на сайт
SESSION_SAVE_EVERY_REQUEST = True

REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_THROTTLE_RATES": {
        "user": "50/m",  # 50 запросов за 30 секунд для зарегистрированных
        "anon": "5/m",  # 5 запросов за 30 секунд для анонимных пользователей
    },
}

# Временное хранилище для ключей кеша, НЕ УДАЛЯТЬ !
# Позже перенесется в ENV
BANNERS_KEY = "banners"
user_comparison_key = "user_comparison_"
anonymous_comparison_key = "anonymous_user_comparison_"
CART_SESSION_ID = "cart"
CATEGORY_CASHING_TIME = 60 * 60 * 24
CATEGORY_KEY = "categories"
PRODUCTS_KEY = "category_{category_id}"
from dotenv import load_dotenv

load_dotenv()
import os

SECRET_KEY_STRIPE = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET_KEY = os.getenv("STRIPE_WEBHOOK_SECRET_KEY")

