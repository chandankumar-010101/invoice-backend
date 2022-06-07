from .base import *
from decouple import config
DEBUG = True

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': config('LOCAL_DB_NAME'), 
        'USER': config('LOCAL_USER'), 
        'PASSWORD': config('LOCAL_PASSWORD'),
        'HOST': config('LOCAL_HOST'), 
        'PORT': config('LOCAL_PORT'),
    }
}