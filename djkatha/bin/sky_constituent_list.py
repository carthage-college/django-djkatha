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
import django
import argparse
import pyodbc
import datetime
from datetime import datetime, timezone
from datetime import date
import time
import arrow
from time import strftime, strptime


# Note to self, keep this here
# django settings for shell environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djkatha.settings.shell")
django.setup()
# ________________
from django.conf import settings
from djkatha.core.sky_api_auth import fn_do_token
from djkatha.core.sky_api_calls import get_constituent_list, \
    get_constituent_custom_fields
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

        Currently the student adds would be periodic
        OMatic processes, but I would possibly need to create the custom field
        Record if OMatic doesn't create it 
        
        May be easiest to just purge the table and repopulate it periodically

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
        # timestamp = date.replace(tzinfo=timezone.utc).timestamp()
        # print(timestamp)
        # ndate = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%f")
        # ndate = datetime.strptime(date, "%Y-%m-%d %H:M:%S.%f-z")

        # Use tool calld Arrow, because BB date formats are a mess
        # creates an Arrow object
        ndate = arrow.get(date)
        # print(ndate)

        # arrow has a datetime for its arrow object
        dt = ndate.datetime

        #Now I have something I can format
        # retdate = datetime.strftime(dt, "%Y-%m-%d")
        retdate = datetime.strftime(dt, "%m/%d/%Y")
        # print(retdate)
    else:
        retdate = ''
    # print(str(date) + ',' + str(retdate))
    return retdate


def fn_insert_local(i):

    try:
        if i['type'] == 'Individual':
            dt_add = fn_convert_date((i['date_added']))
            dt_mod = fn_convert_date((i['date_modified']))
            fullname = i['first'].strip() + ' ' + i['last'].strip()
            print(dt_mod)

            q_ins_sql = '''INSERT INTO cx_sandbox:raisers_edge_id_match 
                (id, re_id, fullname, category, const_type) 
                VALUES(?, ?, ?, ?, ?)'''

            q_ins_args = (i['lookup_id'], i['id'], fullname, 'Student Status',
                          i['type'])

            print(q_ins_sql)
            print(q_ins_args)
            connection = get_connection(EARL)
            with connection:
                cur = connection.cursor()
                cur.execute(q_ins_sql, q_ins_args)
                # connection.commit()

    except pyodbc.Error as err:
        # print("Error in fn_insert_local:  " + str(err))
        sqlstate = err.args[0]
        print(sqlstate)


def fn_update_local(i):
    try:
        bb_id = i['id']
        carth_id = i['lookup_id']
        name = i['first'].strip() + ' ' + i['last'].strip()
        type = i['type']
        dt_add = fn_convert_date((i['date_added']))
        dt_mod = fn_convert_date((i['date_modified']))
        print(dt_mod)
        print(dt_add)

        if type == 'Individual':
            print('UPDATE: Name = ' + name + ', CarthID = ' + str(carth_id)
            + ', BlackbaudID = ' + str(bb_id) + ', type = '
            + type)
        q_upd_sql = '''UPDATE cx_sandbox:raisers_edge_id_match
                SET re_id = ?, fullname = ?, category = ?, const_type = ?, 
                date_added = ?
                WHERE id = ?
                '''
        q_upd_args = (bb_id, name, 'Student Status', type, carth_id, dt_add)
        print(q_upd_args)
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
        #     EARL = settings.INFORMIX_ODBC_TRAIN
        # if database == 'train':
        EARL = settings.INFORMIX_ODBC_TRAIN
        # if database == 'sandbox':
        #     EARL = settings.INFORMIX_ODBC_SANDBOX

        """"--------GET THE TOKEN------------------"""
        current_token = fn_do_token()
        # print("Current Token = ")
        # print(current_token)


        """Here is a question:  There will be over 100k entries in their
            system.  How can I retrieve only students?"""
        """-----Get a list of constituents-------"""
        """---May need this to match Carthage ID to Blackbaud ID------"""
        x = get_constituent_list(current_token)
        for i in x['value']:
            # print(x)
            #     print(i['id'])
            carth_id = i['lookup_id']


            """Will write the BB ID to a table - not yet created
                will be in a mysql database...for now in CX sandbox
            """
            # q_ins_wc = '''
            # INSERT  INTO
            # cc_work_cat_table(work_cat_code, work_cat_descr,
            #                   active_date)
            # VALUES(?, ?, ?)'''
            #     q_ins_wc_args = (workercatcode,workercatdescr,
            #                      datetime.now().strftime("%m/%d/%Y"))
            # engine.execute(q_ins_wc, q_ins_wc_args)
            print(carth_id)

            chk_sql = '''select count(id) from
                cx_sandbox:raisers_edge_id_match
                where id = {}'''.format(carth_id)
            print(chk_sql)
            connection = get_connection(EARL)
            with connection:
                data_result = xsql(chk_sql)
                # print("Query result = " + str(data_result))
                if data_result:
                    for row in data_result:
                        if row[0] == 1:
                            print("Record exists for " + str(carth_id))
                            print("Update")
                            fn_update_local(i)
                        elif row[0] == 0:
                            print("No record for " + str(carth_id))
                            print("Insert")
                            fn_insert_local(i)
                        elif row[0] > 1:
                            print("Error - multiple records for " + str(carth_id))
                else:
                    print("No record for " + str(carth_id))
                    print("Insert")
                    fn_insert_local(i)

                #     connection.cursor.close()

                    # if data_result == 0 or data_result is None:
                    #     print("insert")
                    # else:
                    #     print("update")

                # # For testing and development...
                # ins_sql = '''INSERT INTO cx_sandbox:raisers_edge_id_match
                #            (id, re_id, fullname, category, value, date_added,
                #            date_updated, comment)
                #            VALUES(?,?,?,?,?,?,?,?)'''
                # ins_args = (carth_id, bb_id, name, 'Student Status', type,
                #             '2019-11-13', '2019-11-21', 'Testing an add')
                #
                # print(ins_sql)
                # print(ins_args)

                # try:
                #     cursor = connection.cursor()
                #     # print(connection)
                #     cursor.execute(ins_sql, ins_args)
                #     # with connection:
                #     #     xsql(ins_sql, ins_args)
                #
                # # except connection.cursor.IntegrityError as e:
                # except Exception as e:
                #     print("Error {} ".format(e) )
                # # print(str(sys.exc_info()[:2]))

        # with connection:
        #     data_result = xsql(
        #         ins_sql, connection,
        #         key=settings.INFORMIX_DEBUG
        #     ).fetchall()

        # ret = list(data_result)
        # for i in ret:
        #     print(str(i[0]) + " " + i[1] + " " + i[5])



    except Exception as e:
        print("Error in main:  " + str(e))
        # print(type(e))
        # print(e.args)
        sqlstate = e.args[1]
        print(sqlstate)

        # print(str(e.message))
        # fn_write_error("Error in misc_fees.py - Main: "
        #                + str(e))


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
