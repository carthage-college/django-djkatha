"""SKY API Authentication/Query Scripts
Modified from code by Mitch Hollberg
(mhollberg@gmail.com, mhollberg@cfgreateratlanta.org)
Python functions to
    a) Get an initial SKYApi token/refresh token and write them to a local file
    b) Make subsequent refreshes and updates to the SKYApi authentication
    based on tokens in the files.
"""
 
# import requests
import sys
import os
# import argparse
import pyodbc
import datetime
from datetime import datetime, date, timedelta
from time import strftime, strptime
import django


# Note to self, keep this here
# django settings for shell environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djkatha.settings.shell")
django.setup()
# ________________

# django settings for script
from django.conf import settings
from django.core.cache import cache

from djkatha.core.utilities import fn_write_error, fn_send_mail
from djkatha.core.sky_api_auth import fn_do_token
from djkatha.core.sky_api_calls import get_constituents_custom_field_list, \
    get_lookup_id
from djimix.core.utils import get_connection, xsql

# informix environment
os.environ['INFORMIXSERVER'] = settings.INFORMIXSERVER
os.environ['DBSERVERNAME'] = settings.DBSERVERNAME
os.environ['INFORMIXDIR'] = settings.INFORMIXDIR
os.environ['ODBCINI'] = settings.ODBCINI
os.environ['ONCONFIG'] = settings.ONCONFIG
os.environ['INFORMIXSQLHOSTS'] = settings.INFORMIXSQLHOSTS

# normally set as 'debug" in SETTINGS
DEBUG = settings.INFORMIX_DEBUG
desc = """
    Collect data from Blackbaud
"""


def fn_update_local(carth_id, bb_id, EARL):
    try:

        q_upd_sql = '''UPDATE cvid_rec
                SET re_api_id = ? WHERE cx_id = ?
                '''
        q_upd_args = (bb_id, carth_id)
        connection = get_connection(EARL)
        with connection:
            cur = connection.cursor()
            cur.execute(q_upd_sql, q_upd_args)
            return 1
    except pyodbc.Error as err:
            print("Error in fn_update_local:  " + str(err))
            sqlstate = err.args[0]
            print(sqlstate)
            return 0


def check_for_constituents(EARL):
    try:


        """"--------GET THE TOKEN------------------"""
        current_token = fn_do_token()

        """-----Get a list of constituents with a custom field of 
            Student Status - STORE the id in cvid_rec-------"""
        """---We need this to match Carthage ID to Blackbaud ID------"""

        """
           UPDATE 1/17/20  It will more likely be the case that we will get
           a csv list from advancement of the students added.  If so, we 
           can read that csv and find the BB_ID only for those students"""

        """The date of the last search will be stored in Cache"""
        searchtime = cache.get('last_const_date')


        # API call to get BB ID
        x = get_constituents_custom_field_list(current_token, str(searchtime))
        if x == 0:
            print("No recent student entries in RE")
        else:
            for i in x['value']:
                bb_id = i["parent_id"]
                # Look for ID in cvid_rec
                chk_sql = '''select cx_id, re_api_id from cvid_rec
                    where re_api_id = {}'''.format(i['parent_id'])

                connection = get_connection(EARL)

                with connection:
                    data_result = xsql(chk_sql, connection, key='debug')
                    x = data_result.fetchone()

                    # Create the cvid_rec if it doesn't exist - Will require
                    # second call to API to retrieve the carthage id using
                    # the blackbaud id
                    if x is None:
                        carth_id = get_lookup_id(current_token, bb_id)
                        ret = fn_update_local(carth_id, bb_id, EARL)
                    else:
                        print("CVID Rec exists for" + str(x[0]))
                        # carth_id = x[0]
                        pass



    except Exception as e:
        # print("Error in main:  " + repr(e))
        sqlstate = e.args[1]
        # print(sqlstate)
        fn_write_error("Error in sky_constituent_list.py - Main: "
                       + repr(e))
        fn_send_mail(settings.BB_SKY_TO_EMAIL,
                     settings.BB_SKY_FROM_EMAIL, "SKY API ERROR", "Error in "
                                "sky_constituent_list.py - for: " + + repr(e))
