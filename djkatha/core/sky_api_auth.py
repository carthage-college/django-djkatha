# -*- coding: utf-8 -*-

import datetime
import json
import logging
import os
import requests
import traceback

from django.conf import settings
from django.core.cache import cache
from djkatha.core.utilities import fn_send_mail
from djkatha.core.utilities import fn_write_error

logger = logging.getLogger('debug_logfile')


def fn_token_refresh():
    now = datetime.datetime.now()
    try:
        # Generates a new OAUTH2 access token and refresh token using
        # the current (unexpired) refresh token. Writes updated tokens
        # to appropriate files for subsequent reference
        # :return: Tuple containing (return_code, access_token, refresh_token)
        refresh_token = cache.get(settings.BB_SKY_REFRESH_TOKEN_CACHE_KEY)
        fn_write_error(refresh_token)
        ref_token_call = requests.post(
            url='{0}/token'.format(settings.BB_SKY_OAUTH2_URL),
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

            cache.set(settings.BB_SKY_TOKEN_CACHE_KEY, access_token)
            cache.set(settings.BB_SKY_REFRESH_TOKEN_CACHE_KEY, refresh_token)
            cache.set(settings.BB_SKY_REFRESH_TIME_CACHE_KEY, now)

            return 1

        elif status == 403:  # OUT OF API QUOTA - Quit
            fn_write_error('ERROR:  ' + str(status) + ":"
                           + ' You\'re out of API Quota!')
            fn_send_mail(settings.BB_SKY_TO_EMAIL,
                         settings.BB_SKY_FROM_EMAIL, "SKY API ERROR",
                         'ERROR:  ' + str(status) + ":"
                         + ' You\'re out of API Quota!')
            exit()
            return 0
        else:
            fn_write_error('ERROR eh:  ' + str(status))
            return 0
    except Exception as error:
        fn_write_error("Error in fn_token_refresh() - Main: " + repr(error))
        stack = traceback.print_exc()
        fn_write_error("Stack trace: %s" % repr(stack))
        fn_send_mail(
            settings.BB_SKY_TO_EMAIL,
            settings.BB_SKY_FROM_EMAIL,
            "SKY API ERROR",
            "Error in sky_api_auth.py - fn_token_refresh: %s" % repr(error),
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
    now = datetime.datetime.now()
    #try:
    if True:
        """
        Check to see if the token has expired, if so refresh it
        the token expires in 60 minutes, but the refresh token
        is good for 60 days
        """
        time_refresh = cache.get(settings.BB_SKY_REFRESH_TIME_CACHE_KEY)
        if time_refresh is None:
            token_refresh = fn_token_refresh()
        elif time_refresh < now - datetime.timedelta(minutes=59):
            token_refresh = fn_token_refresh()
        else:
            pass
        """"--------GET THE TOKEN------------------"""
        current_token = cache.get(settings.BB_SKY_TOKEN_CACHE_KEY)
        return current_token
    """
    except Exception as error:
        logger.debug("Error in fn_do_token() - Main: " + repr(error))
        fn_write_error("Error in fn_do_token() - Main: " + repr(error))
        stack = traceback.print_exc()
        fn_write_error("Stack trace: %s" % repr(stack))
        #fn_send_mail(settings.BB_SKY_TO_EMAIL,
        #             settings.BB_SKY_FROM_EMAIL, "SKY API ERROR",
        #             "Error in sky_pi_auth.py - fn_do_token: " + repr(error))
        return 0
    """
