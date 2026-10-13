from .common import *
import os

DEBUG = True
ALLOWED_HOSTS = ['*']

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='brokerdb'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default='123456@Aa'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5555'),
    }
}

# Remove SQLite database file if it exists
sqlite_path = os.path.join(BASE_DIR, 'db.sqlite3')
if os.path.exists(sqlite_path):
    try:
        os.remove(sqlite_path)
    except OSError as e:
        print(f"Error deleting SQLite database file: {e}")
