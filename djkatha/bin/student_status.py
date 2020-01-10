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
from datetime import datetime, timezone
import django
import os.path
import csv
import argparse
import mysql.connector
import pyodbc
import arrow



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
from djkatha.core.sky_api_auth import fn_do_token
from djkatha.core.sky_api_calls import api_get, get_const_custom_fields, \
    get_constituent_id, set_const_custom_field, update_const_custom_fields, \
    delete_const_custom_fields, get_relationships, api_post, api_patch, \
    api_delete, get_custom_fields, get_custom_field_value, get_constituent_list

from djimix.core.utils import get_connection, xsql

# normally set as 'debug" in SETTINGS
DEBUG = settings.INFORMIX_DEBUG
desc = """
    Collect data from Blackbaud
"""
parser = argparse.ArgumentParser(description=desc)

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
    1. Find the status of students in CX, (Look for a change date in 
        audit table)
    2.Then determine if the students with recent changes are in Raiser's Edge
        ***WIll it be possible to have a student in RE w/o a status code?***
        ***Only if student was added as a constituent and not a student***
        ***If so, my table of existing students may be less than perfect***
         
        3a  Look for student in my table with cx and BB id numbers
        3b  If not found, make API call to look for student NOT using status 
            as a filter
        3c If not in BB data pass on the record...will use O-matic to 
           add new students three times a year
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
        # if database == 'sandbox':
        #     EARL = settings.INFORMIX_ODBC_SANDBOX

        else:
            # # this will raise an error when we call get_engine()
            # below but the argument parser should have taken
            # care of this scenario and we will never arrive here.
            EARL = None
        # establish database connection

        '''Steve set up something - 
            But it is more likely we will use cvid_rec to store
            the bb_id 
            else, have to figure out how to use the sql database...'''

        action = ''
        # action = 'set_status'
        # action = 'update_status'

        """"--------GET THE TOKEN------------------"""
        current_token = fn_do_token()
        # print("Current Token = ")
        # print(current_token)

        """
           -----------------------------------------------------------
           ---GET STUDENTS WITH A STATUS CHANGE FROM PROG_ENR_REC-----
           -----------------------------------------------------------
        """

        # for real..
        # statquery = '''select O.id, O.acst, O.audit_event, O.audit_timestamp,
        #     N.id, N.acst, N.audit_event, N.audit_timestamp
        #     from cars_audit:prog_enr_rec N
        #     left join cars_audit:prog_enr_rec O
        #     on O.id = N.id
        #     and O.acst != N.acst
        #     and O.audit_event = 'BU'
        #     where N.audit_event != 'BU'
        #     and N.audit_timestamp > TODAY - 15
        #     and N.audit_timestamp = O.audit_timestamp
        #     '''

        # for testing...
        statquery = '''select PER.id, PER.acst, AST.txt 
            from prog_enr_rec PER
            JOIN acad_stat_table AST
            on AST.acst = PER.acst
            where PER.id in (1357063)'''
            # (select id from cx_sandbox:raisers_edge_id_match) '''
        # print(statquery)

        connection = get_connection(EARL)
        with connection:
            data_result = xsql(statquery).fetchall()
            ret = list(data_result)
            for i in ret:
                print(str(i[0]) + " " + i[1])
                carth_id = i[0]
                acad_stat = i[2]

                # carth_id = 273530
                # # carth_id = 1524365

                """
                   -----------------------------------------------------------
                   ---FIND RAISERS EDGE ID IN LOCAL TABLE --------------------
                   -----------------------------------------------------------
        
                  Look for student and status in local table
                  Dave R. says to add a column to cvid_rec
                  Else look for student and status at BB via API
                  Add to BB if necessary (THIS WILL BE DONE BY OMATIC)
                  Add or update status in BB
                  Update local table if necessary
                """
                """1. Look for id in local table"""
                # initialize bb_id
                bb_id = 0
                chk_sql = '''select re_api_id from
                    cx_sandbox:cvid_rec
                    where cx_id = {}'''.format(carth_id)
                # print(chk_sql)
                connection = get_connection(EARL)
                with connection:
                    data_result = xsql(chk_sql).fetchall()

                    ret = list(data_result)
                    if ret:
                        for j in ret:
                            bb_id = j[0]
                            print(bb_id)

                    else:
                        # Go to the API to see if student is there?
                        print("No bb_id stored locally")
                        bb_id = get_constituent_id(current_token, carth_id)
                        print(bb_id)

                    '''-------------------------------------------------------
                    ---UPDATE THE CUSTOM STUDENT STATUS FIELD-----------------
                    ----------------------------------------------------------
                    '''
                    if bb_id != 0:
                        '''We have to make a call to get the internal id for
                           the custom field entry, then use that to reset it 
                        '''
                        ret = get_const_custom_fields(current_token, bb_id,
                                                      'Student Status')
                        # print(ret)

                        # print("set custom fields: " + str(carth_id) + ", "
                        #       + acad_stat)

                        if ret == 0:
                            print('Add new record')
                        else:
                            print('Update record')

                            # ret = update_const_custom_fields(current_token,
                            #                                  str(ret),
                            #                                  'Test', acad_stat)
                            # print(ret)

                    else:
                        print("Nobody home")


        """
            **************************************
            **************************************
            **************************************
            Here I need to get the local database stuff added
        """


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
