"""
Django settings for ansible_conf project.

Generated by 'django-admin startproject' using Django 3.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""
import environ
from pathlib import Path

env = environ.Env()

environ.Env.read_env('.env')

DEBUG=env.bool('DEBUG', default=False)
IS_PROD=env.bool('IS_PROD', default=False)
SECRET_KEY=env.str('SECRET_KEY', default='DEV1234')

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

if IS_PROD:
    ALLOWED_HOSTS = ["*"] #TODO
else:
    DEBUG = True
    ALLOWED_HOSTS = ["*"]
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django_sass',
    'jsonfield',

    'playbook_generator',
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

ROOT_URLCONF = 'ansible_conf.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': (BASE_DIR.joinpath('templates'),),
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

WSGI_APPLICATION = 'ansible_conf.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

if IS_PROD:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': env('DATABASES_NAME'),
            'USER': env('DATABASES_USER'),
            'PASSWORD': env('DATABASES_PASSWORD'),
            'HOST': env('DATABASES_HOST'),
            'PORT': env('DATABASES_PORT', default='5342'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/
PATH_UPLOAD_CONFIGS = env('PATH_UPLOAD_CONFIGS', default='./')

STATIC_URL = '/static/'

STATIC_ROOT = BASE_DIR.joinpath('../static_root').absolute()

STATICFILES_DIRS = (BASE_DIR.joinpath('static'),)

MEDIA_URL = '/uploads/'

MEDIA_ROOT = PATH_UPLOAD_CONFIGS

STATIC_NODES_CONFIG_PATH = env('STATIC_NODES_CONFIG_PATH', default='/home/jweier/Repo/infrastructureascode-1/ntx2node.yml')

