from .base import *
DEBUG = False
from decouple import config

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': config('TEST_DB_NAME'), 
        'USER': config('TEST_USER'), 
        'PASSWORD': config('TEST_PASSWORD'),
        'HOST': config('TEST_HOST'), 
        'PORT': config('TEST_PORT'),
    }
}
