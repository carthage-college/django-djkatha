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
import argparse
import pyodbc
import datetime
from datetime import datetime, date, timedelta
import arrow
from time import strftime, strptime
import django


# Note to self, keep this here
# django settings for shell environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djkatha.settings.shell")
django.setup()
# ________________
from django.conf import settings
from djkatha.core.sky_api_auth import fn_do_token
from djkatha.core.sky_api_calls import get_constituent_list, \
    get_constituent_custom_fields, get_constituents_custom_field_list, \
    get_constituent_id
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
    12/9/19 - The API call to get_constituent_list can be filtered by student
      status and add date.   
      So the process would involve getting a current list of those with 
      a custom_field_category=Student Status where date added > whatever date
      
      Then I can write the CX id numbers and the Blackbaud ID numbers to a
      file or table, read them back, and use the blackbaud ID to pass any 
      changes to Blackbaud

      The process would have to involve finding the status of active students
      in CX, (Look for a change date...to limit the number.  Maybe audit table)
    
      Then determine if the student is in Raiser's Edge by reading the list
      just retrieved. 

        Currently the student adds would be periodic OMatic processes, 
        but I would possibly need to create the custom field record if 
        OMatic doesn't create it 
        
        May be easiest to just purge the table and repopulate it periodically
        What about graduations then?
        
      If not add student  ??,
          then add the custom field record  ???
      Else - find out of custom field record exists
          If not add
          else update

      So each student will require 1-2 API calls
    
      No way to test any of this because there are no students in RE yet...
"""


def fn_convert_date(date):
    # print(date)
    if date != "":
        '%Y-%m-%dT%H:%M:%S%z'

        # Use tool calld Arrow, because BB date formats are a mess
        # creates an Arrow object
        ndate = arrow.get(date)
        print(ndate)

        # arrow has a datetime for its arrow object
        dt = ndate.datetime

        #Now I have something I can format
        retdate = datetime.strftime(dt, "%m/%d/%Y")
        print(retdate)
    else:
        retdate = ''
    # print(str(date) + ',' + str(retdate))
    return retdate


# def fn_insert_local(i):
#
#     try:
#         if i['type'] == 'Individual':
#             fullname = i['first'].strip() + ' ' + i['last'].strip()
#             id = i['lookup_id']
#             bbid = i['id']
#             typ = i['type']
#
#             q_ins_sql = '''INSERT INTO cvid_rec
#                 (id, re_id, fullname, category, const_type)
#                 VALUES(?, ?, ?, ?, ?)'''
#
#             q_ins_args = (id, bbid,  fullname, 'Student Status',
#                           typ)
#
#             print(q_ins_sql)
#             print(q_ins_args)
#             # connection = get_connection(EARL)
#             # with connection:
#             #     cur = connection.cursor()
#             #     cur.execute(q_ins_sql, q_ins_args)
#             #     # connection.commit()
#
#     except pyodbc.Error as err:
#         # print("Error in fn_insert_local:  " + str(err))
#         sqlstate = err.args[0]
#         print(sqlstate)


def fn_update_local(i):
    try:
        bb_id = i['id']
        carth_id = i['lookup_id']
        name = i['first'].strip() + ' ' + i['last'].strip()
        type = i['type']

        # if type == 'Individual':
        #     print('UPDATE: Name = ' + name + ', CarthID = ' + str(carth_id)
        #     + ', BlackbaudID = ' + str(bb_id) + ', type = '
        #     + type)
        q_upd_sql = '''UPDATE cvid_rec
                SET re_api_id = ? WHERE cx_id = ?
                '''
        q_upd_args = (bb_id, carth_id)
        # q_upd_sql = '''UPDATE raisers_edge_id_match
        #         SET re_id = ?, fullname = ?, category = ?, const_type = ?
        #         WHERE id = ?
        #         '''
        # q_upd_args = (bb_id, name, 'Student Status', type, carth_id)
        # print(q_upd_args)
        connection = get_connection(EARL)
        print(q_upd_sql)
        with connection:
            cur = connection.cursor()
            cur.execute(q_upd_sql, q_upd_args)
    except pyodbc.Error as err:
            # print("Error in fn_update_local:  " + str(err))
            sqlstate = err.args[0]
            print(sqlstate)


def fn_update_local2(carth_id, bb_id):
    try:

        q_upd_sql = '''UPDATE cvid_rec
                SET re_api_id = ? WHERE cx_id = ?
                '''
        q_upd_args = (bb_id, carth_id)
        connection = get_connection(EARL)
        print(q_upd_sql)
        with connection:
            cur = connection.cursor()
            cur.execute(q_upd_sql, q_upd_args)
    except pyodbc.Error as err:
            # print("Error in fn_update_local:  " + str(err))
            sqlstate = err.args[0]
            print(sqlstate)



def main():
    try:
        # set global variable
        global EARL

        # determines which database is being called from the command line
        # if database == 'cars':
        #     EARL = settings.INFORMIX
        # if database == 'train':
        EARL = settings.INFORMIX_ODBC_TRAIN
        # if database == 'sandbox':
        #     EARL = settings.INFORMIX_ODBC_SANDBOX

        """"--------GET THE TOKEN------------------"""
        current_token = fn_do_token()
        # print("Current Token = ")
        # print(current_token)

        # print(EARL)
        """-----Get a list of constituents with a custom field of 
            Student Status-------"""
        """---We need this to match Carthage ID to Blackbaud ID------"""

        searchtime = date.today() + timedelta(days=-10)
        # print("Searchtime = " + str(searchtime))

        """Doing this in reverse by necessity and for logic 
           We only want constituents who have a student status
           So we search for the bb_id for all who have one
           THEN, we can go get the carthage id in a separate step if need be
           We should be able to use a date range to avoid revisiting records"""

        # API call to get BB ID
        x = get_constituents_custom_field_list(current_token, str(searchtime))
        if x == 0:
            print("No Data Returned")
        else:
            # print(x)
            for i in x['value']:
                # print(i['parent_id'])
                # print(i['value'])

                chk_sql = '''select cx_id, re_api_id from cvid_rec
                    where re_api_id = {}'''.format(i['parent_id'])

                # print(chk_sql)
                connection = get_connection(EARL)

                with connection:
                    data_result = xsql(chk_sql, connection, key='debug')
                    if data_result:
                        for row in data_result:
                            carth_id = row[0]
                            # print("Carth ID = " + str(carth_id))

                            if row[0] is not None:
                                print("bbid = " + str(row[1]) + " Carthid = "
                                      + str(row[0]))

                            else:
                                print("Need to find CarthID for bb_id "
                                      + str(row[0]))
                                bb_id = get_constituent_id(current_token,
                                                         carth_id)
                                # print(bb_id)
                                ret = fn_update_local2(carth_id, bb_id)
                                print(ret)

    except Exception as e:
        print("Error in main:  " + str(e))
        # print(type(e))
        # print(e.args)
        sqlstate = e.args[1]
        print(sqlstate)

        # print(str(e.message))
        # fn_write_error("Error in misc_fees.py - Main: "
        #                + str(e))


# def main():
#     try:
#         # set global variable
#         global EARL
#
#         # determines which database is being called from the command line
#         # if database == 'cars':
#         #     EARL = settings.INFORMIX_ODBC_TRAIN
#         # if database == 'train':
#         EARL = settings.INFORMIX_ODBC_TRAIN
#         # if database == 'sandbox':
#         #     EARL = settings.INFORMIX_ODBC_SANDBOX
#
#         """"--------GET THE TOKEN------------------"""
#         current_token = fn_do_token()
#         # print("Current Token = ")
#         # print(current_token)
#
#         # print(EARL)
#         """-----Get a list of constituents with a custom field of
#             Student Status-------"""
#         """---We need this to match Carthage ID to Blackbaud ID------"""
#
#         searchtime = date.today() + timedelta(days=-10)
#         print("Searchtime = " + str(searchtime))
#
#         x = get_constituent_list(current_token, str(searchtime))
#         if x == 0:
#             print("No Data Returned")
#         else:
#             for i in x['value']:
#                 # print(x)
#                 #     print(i['id'])
#                 carth_id = i['lookup_id']
#
#                 print("Date Added = " + str(i['date_added']))
#
#                 """Will write the BB ID to a table - not yet created
#                     will be in a mysql database...for now in CX sandbox
#                 """
#                 # print(carth_id)
#
#                 chk_sql = '''select cx_id, re_api_id from cvid_rec
#                     where cx_id = {}'''.format(carth_id)
#
#                 # print(chk_sql)
#                 connection = get_connection(EARL)
#
#                 with connection:
#                     data_result = xsql(chk_sql, connection, key='debug')
#                     if data_result:
#                         for row in data_result:
#                             # print(str(row[1]))
#                             if row[1] is None:
#                                 print("Add bb_id for " + str(row[0]))
#                                 # fn_update_local(i)
#                             else:
#                                 print("bbid = " + str(i['id']))
#                                 # print("CX Value = " + str(row[1]))
#
#                             # if row[1] == 1:
#                             #     print("Record exists for " + str(carth_id))
#                             #     # should check to see if it matches?
#                             #     print("Update")
#                             #     fn_update_local(i)
#                             # elif row[1] == 0:
#                             #     print("No record for " + str(carth_id))
#                             #     print("Insert")
#                             #     fn_update_local(i)
#                             # elif row[1] > 1:
#                             #     print("Error - multiple records for " + str(carth_id))
#                     else:
#                         print("No cvid record for " + str(carth_id))
#                         # print("Insert")
#                         # fn_insert_local(i)
#
#     except Exception as e:
#         print("Error in main:  " + str(e))
#         # print(type(e))
#         # print(e.args)
#         sqlstate = e.args[1]
#         print(sqlstate)
#
#         # print(str(e.message))
#         # fn_write_error("Error in misc_fees.py - Main: "
#         #                + str(e))


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
