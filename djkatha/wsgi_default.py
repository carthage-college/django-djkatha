# -*- coding: utf-8 -*-

"""WSGI configuration."""

import os
import sys

from django.core.wsgi import get_wsgi_application


# python
sys.path.append('/d2/python_venv/3.6/djthia/lib/python3.6/')
sys.path.append('/d2/python_venv/3.6/djthia/lib/python3.6/site-packages/')
# django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djthia.settings.production')
os.environ.setdefault('PYTHON_EGG_CACHE', '/var/cache/python/.python-eggs')
os.environ.setdefault('TZ', 'America/Chicago')
# informix
os.environ['INFORMIXSERVER'] = ''
os.environ['DBSERVERNAME'] = ''
os.environ['INFORMIXDIR'] = ''
os.environ['ODBCINI'] = ''
os.environ['ONCONFIG'] = ''
os.environ['INFORMIXSQLHOSTS'] = ''
os.environ['LD_LIBRARY_PATH'] = ''
os.environ['LD_RUN_PATH'] = os.environ['LD_LIBRARY_PATH']
# wsgi
application = get_wsgi_application()
