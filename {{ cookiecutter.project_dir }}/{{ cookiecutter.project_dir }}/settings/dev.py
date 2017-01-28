from .base import *


STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static_deploy')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
