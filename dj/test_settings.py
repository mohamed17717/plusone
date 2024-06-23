
# import the base settings
from .settings import *

# stop logging
import logging
logging.disable(logging.CRITICAL)

# Stop debug
DEBUG = False
TEMPLATE_DEBUG = False


# Weak hashing but faster
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Just keep the needed middleware
MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

# Sqlite for simple testing
DATABASES = {
    'default': {
        # [Scalability] Db pool accept too many connections
        # better than normal 'django.db.backends.postgresql'
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'savvy',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'db',
        'PORT': '5432',
        'CONN_MAX_AGE': 600,
        'ATOMIC_REQUESTS': True,
    }
}