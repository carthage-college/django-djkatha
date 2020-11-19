# -*- coding: utf-8 -*-

import base64
import datetime
import json
import os
import requests
import traceback

from django.conf import settings
from django.core.cache import cache
from djkatha.core.utilities import fn_send_mail
from djkatha.core.utilities import fn_write_error


def fn_token_refresh():
    # print("In token_refresh")
    try:
        # Generates a new OAUTH2 access token and refresh token using
        # the current (unexpired) refresh token. Writes updated tokens
        # to appropriate files for subsequent reference
        # :return: Tuple containing (return_code, access_token, refresh_token)
        refresh_token = cache.get('refresh_token')
        # print(refresh_token)
        ref_token_call = requests.post(
            url='https://oauth2.sky.blackbaud.com/token',
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            data={
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token,
                'client_id': settings.BB_SKY_CLIENT_ID,
                ## **** Can we enable this?
                # ***'preserve_refresh_token': 'true',
                'client_secret': settings.BB_SKY_CLIENT_SECRET,
                # 'redirect_uri': settings.BB_SKY_CALLBACK_URI
            },
        )

        status = ref_token_call.status_code
        response = ref_token_call.text

        if status == 200:
            tokens_dict = dict(json.loads(ref_token_call.text))
            refresh_token = tokens_dict['refresh_token']
            access_token = tokens_dict['access_token']

            cache.set('tokenkey', access_token)
            cache.set('refresh_token', refresh_token)
            cache.set('refreshtime', datetime.datetime.now())

            # print(access_token)
            # print(refresh_token)

            return 1

        elif status == 403:  # OUT OF API QUOTA - Quit
            # Print HTML repsonse and exit function with empty DataFrame
            # print('ERROR:  ' + str(status) + ":" + response)
            # print('You\'re out of API Quota!')
            fn_write_error('ERROR:  ' + str(status) + ":"
                           + ' You\'re out of API Quota!')
            fn_send_mail(settings.BB_SKY_TO_EMAIL,
                         settings.BB_SKY_FROM_EMAIL, "SKY API ERROR",
                         'ERROR:  ' + str(status) + ":"
                         + ' You\'re out of API Quota!')
            exit()
            return 0
        else:
            print('here')
            fn_write_error('ERROR:  ' + str(status))
            return 0
    except Exception as error:
        print("Error in token_refresh:  " + error.message)
        fn_write_error("Error in token_refresh.py - Main: " + repr(error))
        stack = traceback.print_exc()
        print(stack)
        fn_write_error("Stack trace: %s" % repr(stack))
        fn_send_mail(
            settings.BB_SKY_TO_EMAIL,
            settings.BB_SKY_FROM_EMAIL,
            "SKY API ERROR",
            "Error in sky_pi_auth.py - fn_token_refresh: %s" % repr(error),
        )
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
        """
        Check to see if the token has expired, if so refresh it
        the token expires in 60 minutes, but the refresh token
        is good for 60 days
        """
        t = cache.get('refreshtime')

        if t is None:
            r = fn_token_refresh()
            print(r)
        elif t < datetime.datetime.now() - datetime.timedelta(minutes=59):
            # print('Out of limit')
            # print(t)
            # print(datetime.datetime.now() - datetime.timedelta(minutes=59))
            r = fn_token_refresh()
            # print(r)
        else:
            # print("within limit")
            pass
        """"--------GET THE TOKEN------------------"""
        current_token = cache.get('tokenkey')
        # print("Current Token = ")
        # print(current_token)
        return current_token

    except Exception as e:
        # print("Error in fn_do_token:  " + repr(e))
        fn_write_error("Error in fn_do_token.py - Main: "
                       + repr(e))
        fn_send_mail(settings.BB_SKY_TO_EMAIL,
                     settings.BB_SKY_FROM_EMAIL, "SKY API ERROR",
                     "Error in sky_pi_auth.py - fn_do_token: " + repr(e))
        return 0


# def main():
#     x = fn_do_token()
#     print("Return = " + str(x))
#
# main()
