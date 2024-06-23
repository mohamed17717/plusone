
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

