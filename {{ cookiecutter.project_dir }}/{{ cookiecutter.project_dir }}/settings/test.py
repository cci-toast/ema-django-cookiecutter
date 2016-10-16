from .dev import *

# Makes tests go a bit faster by using a fast password hasher
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]
