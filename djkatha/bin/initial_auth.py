#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import base64
import cryptography
import datetime
import django
import json
import os
import requests
import sys
import time
from cryptography import fernet

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djkatha.settings.shell')

django.setup()

from django.conf import settings
from django.core.cache import cache


def get_initial_token():
    """Authenticate and generate an OAUTH2 token to the SKY API."""
    # step A - simulate a request from a browser on the authorize_url:
    # will return an authorization code after the user is
    # prompted for credentials.

    authorization_redirect_url = '{0}{1}{2}{3}{4}'.format(
        settings.BB_SKY_AUTHORIZE_URL,
        '?response_type=code&client_id=',
        settings.BB_SKY_CLIENT_ID,
        '&redirect_uri=',
        settings.BB_SKY_CALLBACK_URI,
    )

    print("Click the following url and authorize. It will redirect you to a "
           "blank website with the url"
           " 'https://127.0.0.1/?code=xxxx'. Copy the value of the code "
           "(after the '=' sign). "
           "Paste that code into the prompt below.")
    print("---  {0}  ---".format(authorization_redirect_url))
    authorization_code = input("Paste code here: ")

    # STEP 2: Take initial token, retrieve access codes and floater token
    ref_token_getter = requests.post(
        url=settings.BB_SKY_TOKEN_URL,
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        data={
            'grant_type': 'authorization_code',
            'code': authorization_code,
            'client_id': settings.BB_SKY_CLIENT_ID,
            'client_secret': settings.BB_SKY_CLIENT_SECRET,
            'redirect_uri': settings.BB_SKY_CALLBACK_URI,
        },
    )

    tokens_dict = dict(json.loads(ref_token_getter.text))

    print(tokens_dict)
    refresh_token = tokens_dict['refresh_token']
    access_token = tokens_dict['access_token']

    cache.set('tokenkey', access_token)

    print('token type = {0}'.format(tokens_dict['token_type']))
    print('access token = {0}'.format(cache.get('tokenkey')))
    print('access token expires in = {0} seconds (1 hour)'.format(
        tokens_dict['expires_in'],
    ))
    print('refresh token = {0}'.format(refresh_token))
    print('refresh token expires in = {0} seconds (1 year)'.format(
        tokens_dict['refresh_token_expires_in'],
    ))

    return 1


if __name__ == '__main__':
    sys.exit(get_initial_token())
