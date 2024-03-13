from .base import *

DEBUG = False

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'KEY_PREFIX': 'mysite',  # Префикс для всех ключей кеша
        }
    }
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'mysite',
        'USER': 'mysiteuser',
        'PASSWORD': 'Sharifov1234!',
        'HOST': 'localhost',
        'PORT': '',
    }
}

try:
    from .local import *
except ImportError:
    pass
