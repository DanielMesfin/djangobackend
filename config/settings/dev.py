from .common import *
import os

DEBUG = True
ALLOWED_HOSTS = ['*']

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'brokerdb',
        'USER': 'postgres',
        'PASSWORD': '123456@Aa',
        'HOST': 'localhost',
        'PORT': '5555',
    }
}

# Remove SQLite database file if it exists
sqlite_path = os.path.join(BASE_DIR, 'db.sqlite3')
if os.path.exists(sqlite_path):
    try:
        os.remove(sqlite_path)
    except OSError as e:
        print(f"Error deleting SQLite database file: {e}")
