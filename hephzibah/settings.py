"""
Django settings for the Hephzibah Wears and Collections website.

Configuration that changes between your laptop and a live server (secret
key, debug flag, allowed hosts, email credentials, business contact info)
is read from environment variables / a `.env` file via python-decouple.
See `.env.example` for the full list of variables you can set.
"""

from pathlib import Path
from decouple import config, Csv
import dj_database_url
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Core security settings
# ---------------------------------------------------------------------------

SECRET_KEY = config('SECRET_KEY')

DEBUG = config('DEBUG', cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS').split(",")

# ---------------------------------------------------------------------------
# Application definition
# ---------------------------------------------------------------------------

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',

    'store',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware'
]

ROOT_URLCONF = 'hephzibah.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'store.context_processors.business_info',
                'store.context_processors.categories_menu',
            ],
        },
    },
]

WSGI_APPLICATION = 'hephzibah.wsgi.application'
ASGI_APPLICATION = 'hephzibah.asgi.application'

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
# SQLite is used by default so the project runs with zero extra setup.
# For production, swap this out for Postgres/MySQL (see README.md).

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

DATABASES['default'] = dj_database_url.parse(config("DATABASE_URL"))

# ---------------------------------------------------------------------------
# Password validation
# ---------------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ---------------------------------------------------------------------------
# Internationalization
# ---------------------------------------------------------------------------

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Lagos'
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Static & media files
# ---------------------------------------------------------------------------

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ---------------------------------------------------------------------------
# Uploads
# ---------------------------------------------------------------------------
# Allow reasonably large product photos through (default Django limit is 2.5MB)

DATA_UPLOAD_MAX_MEMORY_SIZE = 20 * 1024 * 1024   # 20 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 20 * 1024 * 1024   # 20 MB

# ---------------------------------------------------------------------------
# Business / brand configuration
# ---------------------------------------------------------------------------
# These power the header/footer, the WhatsApp order buttons, and the
# wholesale enquiry links. Change them in your .env file, not here.

BUSINESS_NAME = config('BUSINESS_NAME', default='Hephzibah Wears and Collections')
BUSINESS_ADDRESS = config('BUSINESS_ADDRESS', default='AA3 Layout, Kuje, Abuja')
BUSINESS_PHONE_DISPLAY = config('BUSINESS_PHONE_DISPLAY', default='+2347082871073')
# Digits only (no +, spaces, or dashes) - this is what wa.me links require.
BUSINESS_WHATSAPP = config('BUSINESS_WHATSAPP', default='2349068832008')
BUSINESS_EMAIL = config('BUSINESS_EMAIL', default='')

# ---------------------------------------------------------------------------
# Email (used only for the wholesale enquiry notification, if configured)
# ---------------------------------------------------------------------------

if config('EMAIL_HOST_USER', default=''):
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
    EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
    EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
    EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
    EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
    DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
else:
    # No SMTP configured: print emails to the console instead of failing.
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

WHOLESALE_NOTIFY_EMAIL = config('WHOLESALE_NOTIFY_EMAIL', default=BUSINESS_EMAIL)

# ---------------------------------------------------------------------------
# Admin branding
# ---------------------------------------------------------------------------

ADMIN_SITE_HEADER = f'{BUSINESS_NAME} Admin'
ADMIN_SITE_TITLE = f'{BUSINESS_NAME} Admin'
ADMIN_INDEX_TITLE = 'Manage products, orders & enquiries'

LOGIN_REDIRECT_URL = '/admin/'
