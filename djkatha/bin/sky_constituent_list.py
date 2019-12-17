"""SKY API Authentication/Query Scripts
Modified from code by Mitch Hollberg
(mhollberg@gmail.com, mhollberg@cfgreateratlanta.org)
Python functions to
    a) Get an initial SKYApi token/refresh token and write them to a local file
    b) Make subsequent refreshes and updates to the SKYApi authentication
    based on tokens in the files.
"""

# from pathlib import Path
import requests
import sys
import os
import json
import time
# import base64
import datetime as dt
import django
import os.path
import csv

# import cryptography
from datetime import datetime

# Note to self, keep this here
# django settings for shell environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djkatha.settings.shell")
django.setup()
# ________________
from django.conf import settings
from django.core.cache import cache
from djkatha.core.sky_api_auth import token_refresh
from djkatha.core.sky_api_calls import get_constituent_list

    # get_const_custom_fields, api_get, \
    # get_constituent_id, set_const_custom_field, update_const_custom_fields, \
    # delete_const_custom_fields, get_relationships, api_post, api_patch, \
    # api_delete, get_custom_fields, get_custom_field_value, get_constituent_list

"""
    12/9/19 - The API call to get_constituent_list can be filtered by student
      status and add date.   
      So the process would involve getting a current list of those with 
      a custom_field_category=Student Status where date added > whatever date
      
      Then I can write the CX id numbers and the Blackbaud ID numbers to a
      file or table, read them back, and use the blackbaud ID to pass any 
      changes to Blackbaud

      The process would have to involve finding the status of active students
      in CX, (Look for a change date...to limit the number.  Maybe audit table)
    
      Then determine if the student is in Raiser's Edge by readint the list
      just retrieved. 
      If not add student, 
         then add the custom field record
      Else - find out of custom field record exists
        If not add
        else update

      So each student will require 1-2 API calls
    
      No way to test any of this because there are no students in RE yet...
"""

def main():
    try:

        action = 'get_constituent_list'

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

        """Check to see if the token has expired, if so refresh it
            the token expires in 60 minutes, but the refresh token
            is good for 60 days"""
        t = cache.get('refreshtime')
        print(t)

        if t is None:
            r = token_refresh()
            print(r)
        elif t < datetime.now() - dt.timedelta(minutes=59):
            print('Out of limit')
            print(t)
            print(datetime.now() - dt.timedelta(minutes=59))
            r = token_refresh()
            print(r)
        else:
            print("within limit")


        """"--------GET THE TOKEN------------------"""
        current_token = cache.get('tokenkey')
        # print("Current Token = ")
        # print(current_token)

        """Here is a question:  There will be over 100k entries in their
            system.  How can I retrieve only students?"""

        if action == 'get_constituent_list':
            """-----Get a list of constituents-------"""
            """---May need this to match Carthage ID to Blackbaud ID------"""
            ret = get_constituent_list(current_token)
            print(ret)

        # """-----Once done, the token must be refreshed-------"""
        # Changed this.   Test at top to see if token has expired, then
        # Refresh the API tokens
        # r = token_refresh()
        # print(r)

    except Exception as e:
        print("Error in main:  " + e.message)
        # fn_write_error("Error in misc_fees.py - Main: "
        #                + e.message)


if __name__ == "__main__":
    # args = parser.parse_args()
    # test = args.test
    # database = args.database

    # if not database:
    #     print "mandatory option missing: database name\n"
    #     parser.print_help()
    #     exit(-1)
    # else:
    #     database = database.lower()

    # if database != 'cars' and database != 'train' and database != 'sandbox':
    #     print "database must be: 'cars' or 'train' or 'sandbox'\n"
    #     parser.print_help()
    #     exit(-1)
    #
    # if not test:
    #     test = 'prod'
    # else:
    #     test = "test"

    sys.exit(main())
