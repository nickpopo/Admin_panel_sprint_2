import os


SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DJANGO_POSTGRES_DBNAME'),
        'USER': os.environ.get('DJANGO_POSTGRES_USER'),
        'PASSWORD': os.environ.get('DJANGO_POSTGRES_PASSWORD'),
        'HOST': os.environ.get('DJANGO_POSTGRES_HOST', '127.0.0.1'),
        'PORT': os.environ.get('DJANGO_POSTGRES_PORT', 5432),
    }   
}
