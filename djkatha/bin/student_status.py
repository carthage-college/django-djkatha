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

        '''For now, possible actions include get_id = which will bypass
          all the others, set_status, update_status, delete_field,
          get_relationships'''

        '''Steve set up something - have to figure out how to call it...'''
        # print(settings.DATABASES)
        # connect = get_connection(settings.DATABASES)
        # cursor = connect.cursor()  # get the cursor
        # cursor.execute("USE default")  # select the database
        # cursor.execute(
        #   "SHOW TABLES")  # execute 'SHOW TABLES' (but data is not returned)

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
            where PER.id in (267310)'''
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
                  Else look for student and status at BB via API
                  Add to BB if necessary (THIS WILL BE DONE BY OMATIC)
                  Add or update status in BB
                  Update local table if necessary
                """
                """1. Look for id in local table"""
                # initialize bb_id
                bb_id = 0
                chk_sql = '''select re_id from
                    cx_sandbox:raisers_edge_id_match
                    where id = {}'''.format(carth_id)
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

                    if bb_id != 0:
                        '''We have to make a call to get the internal id for
                           the custom field entry, then use that to reset it 
                        '''
                        ret = get_const_custom_fields(current_token, bb_id,
                                                      'Student Status')
                        print(ret)

                        print("set custom fields: " + str(carth_id) + ", "
                              + acad_stat)
                        # ret = update_const_custom_fields(current_token,
                        #                                  str(ret),
                        #                                  'Test', acad_stat)
                        # print(ret)
                    else:
                        print("Nobody home")



            # for row in data_result:
                # if row[0] is not None:
                #     const_id = row[0]
                #     category = 'Student Status'
                #     ret = get_const_custom_fields(current_token, const_id,
                #                                   category)
                #     print(ret)
                #     item_id = ret
                #
                #     comment = 'Test 110319'
                #     valu = 'Not a Student'
                #
                #     print("Record exists for " + str(carth_id))
                #     ret = update_const_custom_fields(
                #          current_token, item_id, comment, valu)
                #     print(ret)
                # else:
                #     print("No record for " + str(carth_id))

        """
            **************************************
            **************************************
            **************************************
            Here I need to get the local database stuff added
        """

        # print(settings.SERVER_URL)
        # print(settings.DATABASES['default']['NAME'])
        # nm = settings.DATABASES['default']['NAME']
        # print(settings.MSSQL_EARL)
        # # try:
        # userID = 'brahman'

        # """This works if I can figure out how to find the right
        #     table and schema"""
        # cnxn = pyodbc.connect(settings.MSSQL_EARL)
        # for SQLServer, you must use single quotes in the SQL incantation,
        # otherwise it barfs for some reason
        # sql = "SELECT * FROM fwk_user"
        # sql = "SELECT table_name FROM information_schema.tables"
              # "WHERE table_schema = " + nm
        # table_schema
        # sql = "select  table_name from " \
        #       "information_schema.tables where table_type = 'BASE TABLE' " \
        #       "and table_schema not in ('information_schema','mysql', " \
        #       "'performance_schema','sys') order by table_name;"

        # cursor.execute(sql)
        # rows = cursor.fetchall()
        # cursor.close()
        # # return row[5]
        # for i in rows:
        #     print(i)
        # except:
        #     return None

        # try:
        #     cnx = mysql.connector.connect(
        #                     user=settings.DATABASES['default']['USER'],
        #                     password=settings.DATABASES['default']['PASSWORD'],
        #                     host=settings.DATABASES['default']['HOST'],
        #                     database=settings.DATABASES['default']['NAME']
        #                     )
        #
        # except Exception as e:
        #     # if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        #     #     print("Something is wrong with your user name or password")
        #     # elif err.errno == errorcode.ER_BAD_DB_ERROR:
        #     #     print("Database does not exist")
        #     # else:
        #     print(str(e))
        # else:
        #     cnx.close()

        """
           
             For testing and development...
                 qry = "INSERT INTO cx_sandbox:raisers_edge_id_match
                 (id, re_id, fullname, category, value, date_added, 
                 date_updated, comment)
                 VALUES 
                 (1534657, 20369, 'Bob Amico', 'Student Status', 
                 'Administrator', 
                 '2019-11-13', '2019-11-21', 'Testing an add');"
                connection = get_connection(EARL)
                with connection:
                result = xsql(qry, connection,
                key=settings.INFORMIX_DEBUG
                 ).execute
         """

        """------GET CUSTOM FIELDS FOR A CONSTITUENT----------"""
        # Also need to check to see if the custom field exists
        # Does not appear we can filter by category or type...WHY???
        # NEED TO GRAB THE ITEM ID FROM THE SPECIFIC CUSTOM FIELD
        # NOTE:  There seems to be a delay between successfully creating a
        # custom field value and being able to retrieve it for the student

        """
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
        #     val = 'Active Student'
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
