import os
from .base import *

STATIC_ROOT = os.environ.get('DJANGO_STATIC_ROOT', '/opt/app/static/')
MEDIA_ROOT = os.environ.get('DJANGO_MEDIA_ROOT', '/opt/app/media/')
