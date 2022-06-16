from .base import *
DEBUG = False
from decouple import config

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': config('PRODUCTION_DB_NAME'), 
        'USER': config('PRODUCTION_USER'), 
        'PASSWORD': config('PRODUCTION_PASSWORD'),
        'HOST': config('PRODUCTION_HOST'), 
        'PORT': config('PRODUCTION_PORT'),
    }
}
