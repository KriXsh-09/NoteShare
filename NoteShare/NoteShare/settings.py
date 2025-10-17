# notesshare/settings.py
import os
from pathlib import Path
from decouple import config



BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY')


DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = ['*']


INSTALLED_APPS = [
'django.contrib.admin',
'django.contrib.auth',
'django.contrib.contenttypes',
'django.contrib.sessions',
'django.contrib.messages',
'django.contrib.staticfiles',
'NoteShare.notes.apps.NotesConfig',
'cloudinary_storage',
'cloudinary',
]


MIDDLEWARE = [
'django.middleware.security.SecurityMiddleware',
'whitenoise.middleware.WhiteNoiseMiddleware',
'django.contrib.sessions.middleware.SessionMiddleware',
'django.middleware.common.CommonMiddleware',
'django.middleware.csrf.CsrfViewMiddleware',
'django.contrib.auth.middleware.AuthenticationMiddleware',
'django.contrib.messages.middleware.MessageMiddleware',
'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


ROOT_URLCONF = 'NoteShare.NoteShare.urls'


TEMPLATES = [
{
'BACKEND': 'django.template.backends.django.DjangoTemplates',
'DIRS': [],
'APP_DIRS': True,
'OPTIONS': {'context_processors': [
'django.template.context_processors.debug',
'django.template.context_processors.request',
'django.contrib.auth.context_processors.auth',
'django.contrib.messages.context_processors.messages',
]},
},
]


WSGI_APPLICATION = 'NoteShare.NoteShare.wsgi.application'

import dj_database_url
DATABASES = {
'default': dj_database_url.config(default=config('DATABASE_URL'))
}


AUTH_PASSWORD_VALIDATORS = []


LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [BASE_DIR / 'notes' / 'static']
# Add this line near your STATIC_ROOT setting
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

import cloudinary

cloudinary.config( 
  cloud_name = config('CLOUDINARY_NAME'), 
  api_key = config('CLOUDINARY_API_KEY'), 
  api_secret = config('CLOUDINARY_API_SECRET'), 
  secure = True
)


DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

#MEDIA_URL = '/media/'
#MEDIA_ROOT = BASE_DIR / 'media'

LOGIN_REDIRECT_URL = 'notes:home'
LOGOUT_REDIRECT_URL = 'notes:index'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
