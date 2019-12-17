"""SKY API Authentication/Query Scripts
Modified from code by Mitch Hollberg
(mhollberg@gmail.com, mhollberg@cfgreateratlanta.org)
Python functions to
    a) Get an initial SKYApi token/refresh token and write them to a local file
    b) Make subsequent refreshes and updates to the SKYApi authentication
    based on tokens in the files.
"""

# from pathlib import Path
import os
import sys
import requests
import json
import time
import base64
import datetime as dt
from datetime import datetime
import django
import os.path
import csv
import argparse

# Note to self, keep this here
# django settings for shell environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djkatha.settings.shell")
import django

django.setup()

# django settings for script
from django.conf import settings

# informix environment
os.environ['INFORMIXSERVER'] = settings.INFORMIXSERVER
os.environ['DBSERVERNAME'] = settings.DBSERVERNAME
os.environ['INFORMIXDIR'] = settings.INFORMIXDIR
os.environ['ODBCINI'] = settings.ODBCINI
os.environ['ONCONFIG'] = settings.ONCONFIG
os.environ['INFORMIXSQLHOSTS'] = settings.INFORMIXSQLHOSTS
# ________________
from django.conf import settings
from django.core.cache import cache
from djkatha.core.sky_api_auth import token_refresh
from djkatha.core.sky_api_calls import api_get, get_const_custom_fields, \
    get_constituent_id, set_const_custom_field, update_const_custom_fields, \
    delete_const_custom_fields, get_relationships, api_post, api_patch, \
    api_delete, get_custom_fields, get_custom_field_value, get_constituent_list

from djimix.core.utils import get_connection, xsql

# from djzbar.utils.informix import get_engine
# from djzbar.utils.informix import do_sql
# from djzbar.settings import INFORMIX_EARL_SANDBOX
# from djzbar.settings import INFORMIX_EARL_TEST
# from djzbar.settings import INFORMIX_EARL_PROD
# from djtools.fields import TODAY

# normally set as 'debug" in SETTINGS
DEBUG = settings.INFORMIX_DEBUG
desc = """
    Collect data from Blackbaud
"""
parser = argparse.ArgumentParser(description=desc)

# Test with this then remove, use the standard logging mechanism
# logger = logging.getLogger(__name__)

parser.add_argument(
    "--test",
    action='store_true',
    help="Dry run?",
    dest="test"
)
parser.add_argument(
    "-d", "--database",
    help="database name.",
    dest="database"
)

"""
    The process would have to involve 
    1. Make a call to API periodically to populate local table with BB ID and
        the custom status flag
    2. finding the status of students in CX, 
        (Look for a change date in audit table)
    3.Then determine if the students with recent changes are in Raiser's Edge
         ***WIll it be possible to have a student in RE w/o a status code?***
         ***Only if student was added as a constituent and not a student***
         ***If so, my table of existing students may be less than perfect***
         
         3a  Look for student in my table with cx and BB id numbers
         3b  If not found, make API call to look for student NOT using status 
            as a filter
         3c If not in BB data, add student  
    4 If student was in table, update the custom field
       else If student was just added to BB, add the custom field
            Finally, add student to the local table if new
    --
    No way to test any of this because there are no students in RE yet...
"""


def main():
    try:

        # set global variable
        global EARL

        # determines which database is being called from the command line
        if database == 'cars':
            EARL = settings.INFORMIX_ODBC_TRAIN
        if database == 'train':
            EARL = settings.INFORMIX_ODBC_TRAIN
        if database == 'sandbox':
            EARL = settings.INFORMIX_ODBC_SANDBOX
        else:
            # # this will raise an error when we call get_engine()
            # below but the argument parser should have taken
            # care of this scenario and we will never arrive here.
            EARL = None
        # establish database connection

        # for now, possible actions include get_id = which will bypass
        # all the others, set_status, update_status, delete_field,
        # get_relationships

        # Steve set up something - have to figure out how to call it...
        # print(settings.DATABASES)
        # connect = get_connection(settings.DATABASES)
        # cursor = connect.cursor()  # get the cursor
        # cursor.execute("USE default")  # select the database
        # cursor.execute(
        #     "SHOW TABLES")  # execute 'SHOW TABLES' (but data is not returned)

        action = ''
        # action = 'set_status'
        # action = 'update_status'

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
        if t is None:
            r = token_refresh()
        elif t < datetime.now() - dt.timedelta(minutes=59):
            # print('Out of token refresh limit')
            # print(t)
            # print(datetime.now() - dt.timedelta(minutes=59))
            r = token_refresh()
            # print(r)


        else:
            # print("within token refresh limit")
            pass

        """"--------GET THE TOKEN------------------"""
        current_token = cache.get('tokenkey')
        # print("Current Token = ")
        # print(current_token)


        """ --------GET STUDENTS WITH A STATUS CHANGE -----------------"""
        """        """
        statquery = '''select O.id, O.acst, O.audit_event, O.audit_timestamp,
            N.id, N.acst, N.audit_event, N.audit_timestamp
            from cars_audit:prog_enr_rec N
            left join cars_audit:prog_enr_rec O
            on O.id = N.id
            and O.acst != N.acst
            and O.audit_event = 'BU'
            where N.audit_event != 'BU'
            and N.audit_timestamp > TODAY - 1 
            and N.audit_timestamp = O.audit_timestamp  
            '''

        connection = get_connection(EARL)
        with connection:
            data_result = xsql(
                statquery, connection,
                key=settings.INFORMIX_DEBUG
            ).fetchall()


        # ret = list(data_result)
        # for i in ret:
        #     print(str(i[0]) + " " + i[1] + " " + i[5])
            # Look for student and status in local table
            # Else look for student and status at BB via API
            # Add to BB if necessary
            # Add or update status in BB
            # Update local table if necessary


        """ --------GET THE BLACKBAUD CONSTITUENT ID-----------------"""
        """ I will either have a list of students in a csv file or possibly
            in  a to be determined database
            That way I can get the blackbaud internal id en masse and
            not need to make multiple calls based on the carthage ID
            I may also look to see if the student status has changed in 
            CX
        """

        # #----------------------------------------
        # with open("id_list.csv", 'r') as id_lst:
        #     reed = csv.reader(id_lst, delimiter=',')
        #     for row in reed:
        #         # print(row)
        #         const_id = row[1]
        #
        # # # # First, we have to get the internal ID from blackbaud for
        # # # the constituent
        # # const_id = get_constituent_id(current_token, 1534657)
        # print("Constituent id = " + str(const_id))



        # """------GET CUSTOM FIELDS FOR A CONSTITUENT----------"""
        # # Also need to check to see if the custom field exists
        # # Does not appear we can filter by category or type...WHY???
        # # NEED TO GRAB THE ITEM ID FROM THE SPECIFIC CUSTOM FIELD
        # # NOTE:  There seems to be a delay between successfully creating a
        # # custom field value and being able to retrieve it for the student
        # category = 'Student Status'
        # ret = get_const_custom_fields(current_token, const_id, category)
        # # print(ret)
        # item_id = ret
        # # print("Item ID = " + str(item_id))
        #
        # """
        # --------------------------
        # Here we will need some logic.
        # API options are POST, PATCH, DELETE
        # If the constituent exists and has the specific custom field
        # Student Status, then we need to update
        # the existing record, if not we need to add it
        # ---------------------------
        # """
        #
        # if action == 'set_status':
        #     """-----POST-------"""
        #     # Then we can deal with the custom fields...
        #     comment = 'Testing an add'
        #     val = 'Administrator'
        #     category = 'Student Status'
        #     ret = set_const_custom_field(current_token, const_id, val,
        #                                  category, comment)
        #     print(ret)
        #
        # if action == 'update_status':
        #     """-----PATCH-------"""
        #     # Required:  Token, Item ID
        #     # Need to test to see if all remaining params must be passed or if
        #     # we only pass the ones that change...We shouldn't need to
        #     # change the
        #     # category or type...Would think date added should also
        #     # remain unchanged
        #     # category = 'Involvement'
        #     comment = 'Test 110319'
        #     valu = 'Not a Student'
        #     ret = update_const_custom_fields(current_token, item_id, comment,
        #                                      valu)
        #     print(ret)
        #
        # # """ --------These are generic and not specific to a constituent---"""
        # # ret = get_custom_fields(current_token)
        # # ret = get_custom_field_value(current_token, 'Involvment')
        # #----------------------------------------

    except Exception as e:
        print("Error in main:  " + str(e))
        # fn_write_error("Error in misc_fees.py - Main: "
        #                + e.message)


if __name__ == "__main__":
    args = parser.parse_args()
    test = args.test
    database = args.database

    if not database:
        print("mandatory option missing: database name\n")
        parser.print_help()
        exit(-1)
    else:
        database = database.lower()

    if database != 'cars' and database != 'train' and database != 'sandbox':
        print("database must be: 'cars' or 'train' or 'sandbox'\n")
        parser.print_help()
        exit(-1)

    if not test:
        test = 'prod'
    else:
        test = "test"

    sys.exit(main())
