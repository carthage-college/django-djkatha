# from pathlib import Path
import requests
import os
import json
import base64
import django

# import time
# import datetime
import datetime as dt
from datetime import datetime

# Note to self, keep this here
# django settings for shell environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djequis.settings")
django.setup()

from django.conf import settings
from django.core.cache import cache

AUTHORIZATION = 'Basic ' + settings.BB_SKY_CLIENT_ID + ":" + settings.BB_SKY_CLIENT_SECRET
urlSafeEncodedBytes = base64.urlsafe_b64encode(AUTHORIZATION.encode("utf-8"))
urlSafeEncodedStr = str(urlSafeEncodedBytes)


def fn_token_refresh():
    # print("In token_refresh")
    try:
        # Generates a new OAUTH2 access token and refresh token using
        # the current (unexpired) refresh token. Writes updated tokens
        # to appropriate files for subsequent reference
        # :return: Tuple containing (return_code, access_token, refresh_token)
        refresh_token = cache.get('refreshkey')
        # print(refresh_token)
        ref_token_call = requests.post(
            url='https://oauth2.sky.blackbaud.com/token',
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            data={'grant_type': 'refresh_token',
                  'refresh_token': refresh_token,
                  'client_id': settings.BB_SKY_CLIENT_ID,
                  ## **** Can we enable this?
                  # ***'preserve_refresh_token': 'true',
                  'client_secret': settings.BB_SKY_CLIENT_SECRET,
                  # 'redirect_uri': settings.BB_SKY_CALLBACK_URI
                  }
        )

        status = ref_token_call.status_code
        response = ref_token_call.text

        if status == 200:
            tokens_dict = dict(json.loads(ref_token_call.text))
            refresh_token = tokens_dict['refresh_token']
            access_token = tokens_dict['access_token']

            cache.set('tokenkey', access_token)
            cache.set('refreshkey', refresh_token)
            cache.set('refreshtime', datetime.now())

            # print(access_token)
            # print(refresh_token)

            return 1

        elif status == 403:  # OUT OF API QUOTA - Quit
            # Print HTML repsonse and exit function with empty DataFrame
            print('ERROR:  ' + str(status) + ":" + response)
            print('You\'re out of API Quota!')
            exit()
            return 0
        else:
            print('ERROR:  ' + str(status) + ":" + response)
            return 0
    except Exception as e:
        print("Error in token_refresh:  " + e.message)
        # fn_write_error("Error in fn_do_token.py - Main: "
        #                + e.message)
        return 0

def fn_do_token():
    """--------REFRESH THE TOKEN------------------"""
    """ Because the token only lasts for 60 minutes when things are idle
        it will be necessary to refresh the token before attempting
        anything else.   The refresh token will be valid for 60 days,
        so it should return a new token with no problem.  All the API
        calls will get new tokens, resetting the 60 minute clock, 
        so to avoid calling for a token every time, I may have to 
        either set a timer or see if I can read the date and time from the
        cache files and compare to current time
     """
    try:
        """Check to see if the token has expired, if so refresh it
            the token expires in 60 minutes, but the refresh token
            is good for 60 days"""
        t = cache.get('refreshtime')
        print(t)

        if t is None:
            r = fn_token_refresh()
            print(r)
        elif t < datetime.now() - dt.timedelta(minutes=59):
            print('Out of limit')
            print(t)
            print(datetime.now() - dt.timedelta(minutes=59))
            r = fn_token_refresh()
            print(r)
        else:
            print("within limit")

        """"--------GET THE TOKEN------------------"""
        current_token = cache.get('tokenkey')
        # print("Current Token = ")
        # print(current_token)
        return current_token

    except Exception as e:
        print("Error in fn_do_token:  " + e.message)
        # fn_write_error("Error in fn_do_token.py - Main: "
        #                + e.message)
        return 0

# def main():
#     x = fn_do_token()
#     print("Return = " + str(x))
#
# main()

