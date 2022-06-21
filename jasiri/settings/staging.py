from .base import *
from decouple import config
DEBUG = True

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': config('STAGING_DB_NAME'), 
        'USER': config('STAGING_USER'), 
        'PASSWORD': config('STAGING_PASSWORD'),
        'HOST': config('STAGING_HOST'), 
        'PORT': config('STAGING_PORT'),
    }
}
