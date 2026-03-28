from pathlib import Path
import os
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'dev-open-secret-key')
DEBUG = os.environ.get('DJANGO_DEBUG', '1') == '1'
ALLOWED_HOSTS = [host.strip() for host in os.environ.get('DJANGO_ALLOWED_HOSTS', '*').split(',') if host.strip()]

# close_side/accounts を参照できるようにする
sys.path.append(str(BASE_DIR.parent / "close_side"))

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    "accounts",
    'open_app',
]

AUTHENTICATION_BACKENDS = [
    "accounts.backends.UserCodeOrUsernameBackend",
    "django.contrib.auth.backends.ModelBackend",
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'open_side.urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'open_side.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB', 'dmz_close'),
        'USER': os.environ.get('POSTGRES_USER', 'dmz_app'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'change-me'),
        'HOST': os.environ.get('POSTGRES_HOST', '127.0.0.1'),
        'PORT': os.environ.get('POSTGRES_PORT', '5432'),
        'CONN_MAX_AGE': int(os.environ.get('POSTGRES_CONN_MAX_AGE', '60')),
        'OPTIONS': {
            'sslmode': os.environ.get('POSTGRES_SSLMODE', 'prefer'),
        },
    }
}

LANGUAGE_CODE = 'ja'
TIME_ZONE = 'Asia/Tokyo'
USE_I18N = True
USE_TZ = True
STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
#LOGIN_URL = '/admin/login/'

LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/login/"


# DMZ_BASE = Path(os.environ.get('DMZ_BASE', '/srv/dmz'))
DMZ_BASE = Path(os.environ.get('DMZ_BASE', '/home/ssk11/dmz'))
DMZ_CLOSE_TO_OPEN_PENDING = DMZ_BASE / 'close_to_open' / 'pending'
DMZ_CLOSE_TO_OPEN_PROCESSING = DMZ_BASE / 'close_to_open' / 'processing'
DMZ_OPEN_TO_CLOSE_RETURNED = DMZ_BASE / 'open_to_close' / 'returned'
for path in [DMZ_CLOSE_TO_OPEN_PENDING, DMZ_CLOSE_TO_OPEN_PROCESSING, DMZ_OPEN_TO_CLOSE_RETURNED]:
    path.mkdir(parents=True, exist_ok=True)
