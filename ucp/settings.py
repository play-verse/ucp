"""
Django settings for ucp project.

Generated by 'django-admin startproject' using Django 2.2.16.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
from django.contrib.messages import constants as messages

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '=l&0p&$uc_v8z5!5e8tynb$zjsz0x+-c(2qtnr-&v7f9#no1c7'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'main',
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

ROOT_URLCONF = 'ucp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ucp.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
        'HOST': '127.0.0.1',
        'NAME': 'pv_ucp',
        'USER': 'root',
        'PASSWORD': '',
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Jakarta'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

# Database Extended Constant
NAMA_DATABASE_SAMP = "server_samp"
NAMA_DATABASE_FORUM = "forum"

# SA-MP Constant
SKIN_LIST_MALE = (
    1, 2, 7, 14, 15, 17, 19, 20, 21, 22, 24, 25, 27, 28, 30, 47, 48,
    60, 68, 67, 72, 73, 98, 101, 125, 142, 143, 170, 179, 183, 184
)

SKIN_LIST_FEMALE = (
    9, 11, 12, 13, 40, 41, 54, 55, 56, 69, 76, 141, 148, 150, 151,
    157, 172, 190, 191, 192, 193, 194, 195, 198, 201, 211, 225, 233, 226, 298
)

SPAWN_POINT_REGISTER = (
    {
        "nama": "Pantai St. Maria",
        "x": "288.5987",
        "y": "-1984.3574",
        "z": "2.4633",
        "a": "357.0744",
    },
    {
        "nama": "Kereta Api",
        "x": "1754.5775",
        "y": "-1898.9517",
        "z": "13.5615",
        "a": "269.7162",
    },
    {
        "nama": "Bandara Los Santos",
        "x": "1649.4506",
        "y": "-2329.8547",
        "z": "13.5469",
        "a": "7.0336",
    },
)

MESSAGE_TAGS = {
    messages.ERROR: 'red',
    messages.SUCCESS: 'green',
}

DEFAULT_LIMIT_ITEM = 150

DEFAULT_RESET_RANK = 60 * 5 # Dalam satuan detik
RANK_JSON_TEMPLATE = {
    "lastupdate": 0,
    "data": []
}