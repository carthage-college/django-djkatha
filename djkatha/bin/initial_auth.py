# from pathlib import Path
import requests
import os
import json
import time
import base64
import datetime
import cryptography
import django
from cryptography import fernet
from cryptography.fernet import Fernet
# Note to self, keep this here
# django settings for shell environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djequis.settings")
django.setup()
# ________________
from django.conf import settings
from django.core.cache import cache

AUTHORIZATION = 'Basic ' + settings.BB_SKY_CLIENT_ID + ":" \
                + settings.BB_SKY_CLIENT_SECRET
urlSafeEncodedBytes = base64.urlsafe_b64encode(AUTHORIZATION.encode("utf-8"))
urlSafeEncodedStr = str(urlSafeEncodedBytes)
# print(urlSafeEncodedStr)

# For Cryptography,
# This only needs to happen once...store and re-use
key = fernet.Fernet.generate_key()
type(key)
# file = open('key.key', 'wb') # wb = write bytes
# file.write(key)
# file.close()

def get_initial_token():
    """
    Execute process for user to authenticate and generate an OAUTH2
     token to the SKY API
    """
    # step A - simulate a request from a browser on the authorize_url:
    # will return an authorization code after the user is
    # prompted for credentials.

    authorization_redirect_url = settings.BB_SKY_AUTHORIZE_URL + \
                                 '?response_type=code&client_id=' + \
                                 settings.BB_SKY_CLIENT_ID + '&redirect_uri=' \
                                 + settings.BB_SKY_CALLBACK_URI

    print("Click the following url and authorize. It will redirect you to a "
           "blank website with the url"
           " 'https://127.0.0.1/?code=xxxx'. Copy the value of the code "
           "(after the '=' sign). "
           "Paste that code into the prompt below.")

    print("---  " + authorization_redirect_url + "  ---")
    authorization_code = input("Paste code here: ")

    # print("Authorization Code = ")
    # print(authorization_code)

    # STEP 2: Take initial token, retrieve access codes and floater token
    ref_token_getter = requests.post(
        url='https://oauth2.sky.blackbaud.com/token',
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        data={'grant_type': 'authorization_code',
              'code': authorization_code,
              'client_id': settings.BB_SKY_CLIENT_ID,
              'client_secret': settings.BB_SKY_CLIENT_SECRET,
              'redirect_uri': settings.BB_SKY_CALLBACK_URI}
    )

    tokens_dict = dict(json.loads(ref_token_getter.text))
    # print(tokens_dict)

    frn = fernet.Fernet(key)

    # print("-------------------------------")
    refresh_token = tokens_dict['refresh_token']
    # refresh_token_encrpt = frn.encrypt(refresh_token.encode('ASCII'))
    access_token = tokens_dict['access_token']
    # access_token_encrypt = frn.encrypt(access_token.encode('ASCII'))

    cache.set('tokenkey', access_token)

    #     cache.set('refreshkey', refresh_token)

    x = cache.get('tokenkey')
    y = cache.get('refreshkey')
    # print(x)
    # print(y)

    return 1


def main():
    ret = get_initial_token()
    # print(ret)

main()