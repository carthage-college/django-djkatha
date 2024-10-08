# -*- coding: utf-8 -*-

"""Django settings for project."""

import os
import saml2
import saml2.saml

from pwd import getpwuid
# sqlserver connection string
from djimix.settings.local import MSSQL_EARL
from djimix.settings.local import INFORMIX_ODBC, INFORMIX_ODBC_TRAIN
from djimix.settings.local import (
    INFORMIXSERVER,
    DBSERVERNAME,
    INFORMIXDIR,
    ODBCINI,
    ONCONFIG,
    INFORMIXSQLHOSTS,
    LD_LIBRARY_PATH,
    LD_RUN_PATH
)
# Debug
DEBUG = False
INFORMIX_DEBUG = 'debug'
ADMINS = (
    ('', ''),
)
MANAGERS = ADMINS
SECRET_KEY = ''
ALLOWED_HOSTS = []
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Chicago'
SITE_ID = 1
USE_I18N = False
USE_L10N = False
USE_TZ = False
DEFAULT_CHARSET = 'utf-8'
FILE_CHARSET = 'utf-8'
SERVER_URL = ''
API_URL = '{0}/{1}'.format(SERVER_URL, 'api')
LIVEWHALE_API_URL = 'https://{0}'.format(SERVER_URL)
ROOT_URLCONF = 'djkatha.urls'
WSGI_APPLICATION = 'djkatha.wsgi.application'
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = BASE_DIR
PROJECT_APP = os.path.basename(BASE_DIR)
ROOT_URL = '/{0}/'.format(PROJECT_APP)
ADMIN_MEDIA_PREFIX = '/static/admin/'
MEDIA_ROOT = '{0}/assets/'.format(ROOT_DIR)
STATIC_ROOT = '{0}/static/'.format(ROOT_DIR)
STATIC_URL = '/static/{0}/'.format(PROJECT_APP)
MEDIA_URL = '/media/{0}/'.format(PROJECT_APP)
UPLOADS_DIR = '{0}files/'.format(MEDIA_ROOT)
UPLOADS_URL = '{0}files/'.format(MEDIA_URL)
STATICFILES_DIRS = ()
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
DATABASES = {
    'default': {
        'HOST': '127.0.0.1',
        'PORT': '3306',
        'NAME': 'django_{0}'.format(PROJECT_APP),
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'django_{0}'.format(PROJECT_APP),
        'PASSWORD': ''
    },
}
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    # saml2
    #'djangosaml2',
    # needed for template tags
    'djtools',
    # gmail api for send mail
    'gmailapi_backend',
    # sign in as a user
    'loginas',
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

#MIDDLEWARE.append('djangosaml2.middleware.SamlSessionMiddleware')

# saml2 settings
SAML_SESSION_COOKIE_NAME = 'saml_session'
SAML_SESSION_COOKIE_SAMESITE = 'Lax'
SAML_DEFAULT_BINDING = saml2.BINDING_HTTP_POST
SAML_LOGOUT_REQUEST_PREFERRED_BINDING = saml2.BINDING_HTTP_POST
SAML_IGNORE_LOGOUT_ERRORS = True
SAML_DJANGO_USER_MAIN_ATTRIBUTE = 'email'
SAML_DJANGO_USER_MAIN_ATTRIBUTE_LOOKUP = '__iexact'
SAML_CREATE_UNKNOWN_USER = True
ACS_DEFAULT_REDIRECT_URL = ROOT_URL
SAML_ATTRIBUTE_MAPPING = {
    'cn': ('username', ),
    'mail': ('email', ),
    'givenName': ('first_name', ),
    'sn': ('last_name', ),
}
SAML_CSP_HANDLER=''
# template stuff
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
            '/data2/django_templates/djkali/',
            '/data2/django_templates/djcher/',
            '/data2/django_templates/',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'debug':DEBUG,
            'context_processors': [
                'djtools.context_processors.sitevars',
                'djkatha.context_processors.sitevars',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
            ],
            #'loaders': [
            #    # insert your TEMPLATE_LOADERS here
            #]
        },
    },
]
# caching
__USERNAME = getpwuid(os.getuid()).pw_name
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/var/tmp/django_{0}_cache'.format(PROJECT_APP),
        'TIMEOUT': None,
        'KEY_PREFIX': '{0}_'.format(PROJECT_APP),
        'OPTIONS': {
           'MAX_ENTRIES': 80000,
        }
    }
}
CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True
# LDAP Constants
LDAP_SERVER = ''
LDAP_SERVER_PWM = ''
LDAP_PORT = ''
LDAP_PORT_PWM = ''
LDAP_PROTOCOL = ''
LDAP_PROTOCOL_PWM = ''
LDAP_BASE = ''
LDAP_USER = ''
LDAP_PASS = ''
LDAP_EMAIL_DOMAIN = ''
LDAP_OBJECT_CLASS = ''
LDAP_OBJECT_CLASS_LIST = []
LDAP_GROUPS = {}
LDAP_RETURN = []
LDAP_RETURN_PWM = []
LDAP_ID_ATTR = ''
LDAP_CHALLENGE_ATTR = ''
LDAP_AUTH_USER_PK = False
# auth backends
AUTHENTICATION_BACKENDS = (
    #'djangosaml2.backends.Saml2Backend',
    'djauth.backends.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
)
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LOGIN_URL = '/saml2/login/'

#LOGIN_URL = '{0}accounts/login/'.format(ROOT_URL)
#LOGOUT_URL = '{0}accounts/logout/'.format(ROOT_URL)
LOGIN_REDIRECT_URL = ROOT_URL


USE_X_FORWARDED_HOST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_DOMAIN='.carthage.edu'
SESSION_COOKIE_NAME ='django_{0}_cookie'.format(PROJECT_APP)
SESSION_COOKIE_AGE = 86400
SESSION_COOKIE_SECURE = True
# gmail API settings
EMAIL_FROM = ''
GMAIL_USER = ''
EMAIL_BACKEND = 'gmailapi_backend.service.GmailApiBackend'
GMAIL_SCOPES = ['https://www.googleapis.com/auth/gmail.send']
GMAIL_SERVICE_ACCOUNT_JSON = ''
GOOGLE_SERVICE_ACCOUNT = ''
# system emails
DEFAULT_FROM_EMAIL = ''
SERVER_EMAIL = ''
SERVER_MAIL=''
# logging
LOG_FILEPATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs/',
)
LOG_FILENAME = '{0}{1}'.format(LOG_FILEPATH, 'debug.log')
DEBUG_LOG_FILENAME = LOG_FILEPATH + 'debug.log'
INFO_LOG_FILENAME = LOG_FILEPATH + 'info.log'
ERROR_LOG_FILENAME = LOG_FILEPATH + 'error.log'
CUSTOM_LOG_FILENAME = LOG_FILEPATH + 'custom.log'
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s',
            'datefmt': '%Y/%b/%d %H:%M:%S',
        },
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s',
            'datefmt': '%Y/%b/%d %H:%M:%S',
        },
        'simple': {
            'format': '%(levelname)s %(message)s',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'logfile': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': LOG_FILENAME,
            'formatter': 'standard',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'include_html': True,
            'class': 'django.utils.log.AdminEmailHandler',
        },
    },
    'loggers': {
        'custom_logfile': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': CUSTOM_LOG_FILENAME,
            'formatter': 'custom',
        },
        'info_logfile': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'backupCount': 10,
            'maxBytes': 50000,
            'filename': INFO_LOG_FILENAME,
            'formatter': 'simple',
        },
        'debug_logfile': {
            'level': 'DEBUG',
            'handlers': ['logfile'],
            'class': 'logging.FileHandler',
            'filename': DEBUG_LOG_FILENAME,
            'formatter': 'verbose',
        },
        'error_logfile': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': ERROR_LOG_FILENAME,
            'formatter': 'verbose',
        },
        'django': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'WARN',
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}

# app settings
MANAGERS_GROUP = 'Managers'
# giving day
GIVING_DAY_APPEAL_ID = 0
GIVING_DAY_TICKER_LIMIT = 30
GIVING_DAY_GOALS = {
    '420': {
        'goal': '666',
        'earl': '/giving/give-today/',
    },
}
GIVING_DAY_START_DATE = None
GIVING_DAY_END_DATE = None

# Blackbaud Sky API
# ---------------------------
# To test against the test database, is first necessary to go through the
# process of getting the initial authorization (see bin/initial_auth.py) and
# then to make use of the other client ID and secret key
# To flip back to the live environment, must do that again.

BB_SKY_CLIENT_ID = ''
BB_SKY_CLIENT_SECRET = ''
BB_SKY_TOKEN_FILE = ''
BB_SKY_TOKEN_CACHE_KEY = 'tokenkey'
BB_SKY_REFRESH_TOKEN_FILE = ''
BB_SKY_REFRESH_TOKEN_CACHE_KEY = 'refresh_token'
BB_SKY_REFRESH_TIME_CACHE_KEY = 'refreshtime'
BB_SKY_CALLBACK_URI = ''
BB_SKY_OAUTH2_URL = 'https://oauth2.sky.blackbaud.com'
BB_SKY_AUTHORIZE_URL = '{0}/authorization'.format(BB_SKY_OAUTH2_URL)
BB_SKY_TOKEN_URL = '{0}/token'.format(BB_SKY_OAUTH2_URL)
BB_SKY_API_URL = 'https://api.sky.blackbaud.com'
BB_SKY_SUBSCRIPTION_KEY = ''
BB_LOG_FOLDER = ''
BB_SKY_TO_EMAIL = ''
BB_SKY_FROM_EMAIL = ''


##################
# LOCAL SETTINGS #
##################

# Allow any settings to be defined in local.py which should be
# ignored in your version control system allowing for settings to be
# defined per machine.

# Instead of doing "from .local import *", we use exec so that
# local has full access to everything defined in this module.
# Also force into sys.modules so it's visible to Django's autoreload.

phile = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'local.py')
if os.path.exists(phile):
    import imp
    import sys
    module_name = '{0}.settings.local'.format(PROJECT_APP)
    module = imp.new_module(module_name)
    module.__file__ = phile
    sys.modules[module_name] = module
    exec(open(phile, 'rb').read())
