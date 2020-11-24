"""
Django settings for project.
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

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
API_URL = '{}/{}'.format(SERVER_URL, 'api')
LIVEWHALE_API_URL = 'https://{}'.format(SERVER_URL)
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
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)
DATABASES = {
    'default': {
        'HOST': '127.0.0.1',
        'PORT': '3306',
        'NAME': 'django_djkatha',
        'ENGINE': 'django.db.backends.mysql',
        'USER': '',
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
    # needed for template tags
    'djtools',
    # honeypot for admin attacks
    'admin_honeypot',
    # sign in as a user
    'loginas',
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # the following should be uncommented unless you are
    # embedding your apps in iframes
    #'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
# template stuff
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
            '/data2/django_templates/djkorra/',
            '/data2/django_templates/djbootmin/',
            '/data2/django_templates/djcher/',
            '/data2/django_templates/django-djskins/',
            '/data2/livewhale/includes/',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'debug':DEBUG,
            'context_processors': [
                'djtools.context_processors.sitevars',
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
CACHES = {
    'default': {
        # 'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        #'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        #'LOCATION': '127.0.0.1:11211',
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/var/tmp/django_djkatha_cache',
        'TIMEOUT': None,
        'KEY_PREFIX': 'djkatha_',
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
    'djauth.ldapBackend.LDAPBackend',
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
LOGIN_URL = '{0}accounts/login/'.format(ROOT_URL)
LOGOUT_URL = '{0}accounts/logout/'.format(ROOT_URL)
LOGIN_REDIRECT_URL = ROOT_URL
USE_X_FORWARDED_HOST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_DOMAIN='.carthage.edu'
SESSION_COOKIE_NAME ='django_djkatha_cookie'
SESSION_COOKIE_AGE = 86400
# SMTP settings
EMAIL_HOST = ''
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_FAIL_SILENTLY = False
DEFAULT_FROM_EMAIL = ''
SERVER_EMAIL = ''
SERVER_MAIL=''
# logging
LOG_FILEPATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs/')
DEBUG_LOG_FILENAME = LOG_FILEPATH + 'debug.log'
INFO_LOG_FILENAME = LOG_FILEPATH + 'info.log'
ERROR_LOG_FILENAME = LOG_FILEPATH + 'error.log'
CUSTOM_LOG_FILENAME = LOG_FILEPATH + 'custom.log'
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format' : '[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s',
            'datefmt' : '%Y/%b/%d %H:%M:%S'
        },
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s',
            'datefmt' : '%Y/%b/%d %H:%M:%S'
        },
        'custom': {
            'format': '%(asctime)s: %(levelname)s: %(message)s',
            'datefmt' : '%m/%d/%Y %I:%M:%S %p'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'custom_logfile': {
            'level':'ERROR',
            'filters': ['require_debug_true'], # do not run error logger in production
            'class': 'logging.FileHandler',
            'filename': CUSTOM_LOG_FILENAME,
            'formatter': 'custom',
        },
        'info_logfile': {
            'level':'INFO',
            'class':'logging.handlers.RotatingFileHandler',
            'backupCount': 10,
            'maxBytes': 50000,
            'filters': ['require_debug_false'], # run logger in production
            'filename': INFO_LOG_FILENAME,
            'formatter': 'simple',
        },
        'debug_logfile': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'], # do not run debug logger in production
            'class': 'logging.FileHandler',
            'filename': DEBUG_LOG_FILENAME,
            'formatter': 'verbose'
        },
        'error_logfile': {
            'level': 'ERROR',
            #'filters': ['require_debug_true'], # do not run error logger in production
            'class': 'logging.FileHandler',
            'filename': ERROR_LOG_FILENAME,
            'formatter': 'verbose'
        },
        'console':{
            'level':'INFO',
            'class':'logging.StreamHandler',
            'formatter': 'standard'
        },
        'mail_admins': {
            'level': 'ERROR',
            #'filters': ['require_debug_false'],
            'include_html': True,
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'redpanda': {
            'handlers':['debug_logfile'],
            'propagate': True,
            'level':'DEBUG',
        },
        'redpanda.lynx': {
            'handlers':['debug_logfile'],
            'propagate': True,
            'level':'DEBUG',
        },
        'redpanda.core': {
            'handlers':['debug_logfile'],
            'propagate': True,
            'level':'DEBUG',
        },
        'error_logger': {
            'handlers': ['error_logfile'],
            'level': 'ERROR'
         },
        'info_logger': {
            'handlers': ['info_logfile'],
            'level': 'INFO'
        },
        'debug_logger': {
            'handlers':['debug_logfile'],
            'propagate': True,
            'level':'DEBUG',
        },
        'django': {
            'handlers':['console'],
            'propagate': True,
            'level':'WARN',
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['mail_admins', 'error_logfile'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

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
