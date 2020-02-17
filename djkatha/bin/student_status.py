"""SKY API Authentication/Query Scripts
Modified from code by Mitch Hollberg
(mhollberg@gmail.com, mhollberg@cfgreateratlanta.org)
Python functions to
    a) Get an initial SKYApi token/refresh token and write them to a local file
    b) Make subsequent refreshes and updates to the SKYApi authentication
    based on tokens in the files.
"""

import os
import sys
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
    2. Then determine if the students with recent changes are in Raiser's Edge
        ***WIll it be possible to have a student in RE w/o a status code?***
        ***Only if student was added as a constituent and not a student***
        ***If so, my table of existing students may be less than perfect***
         
        2a  Look for student in my table with cx and BB id numbers
        2b  If not found, make API call to look for student NOT using status 
            as a filter
        2c If not in BB data pass on the record...will use O-matic to 
           add new students three times a year
    3. If student was in table, update the custom field
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
            EARL = settings.INFORMIX_ODBC
        if database == 'train':
            EARL = settings.INFORMIX_ODBC_TRAIN
        if database == 'sandbox':
            EARL = settings.INFORMIX_ODBC_SANDBOX

        # else:
            # # this will raise an error when we call get_engine()
            # below but the argument parser should have taken
            # care of this scenario and we will never arrive here.
            # EARL = None
        # establish database connection

        """"--------GET THE TOKEN------------------"""
        current_token = fn_do_token()
        # print("Current Token = ")
        # print(current_token)

        """
           -----------------------------------------------------------
           -1-GET STUDENTS WITH A STATUS CHANGE FROM PROG_ENR_REC-----
           -----------------------------------------------------------
        """
        print(EARL)
        # for real..
        # Two options.  Get all changed records, look for local BB ID but ALSO
        # look for BB ID via API.  If there is a record in BB, then add the
        # BB ID locally if it doesn't exist.
        # OR
        # Ignore all changes locally that do not match an existing local BB ID
        # The latter would be the lowest hits on the API
        # statquery = '''select O.id, O.acst, O.audit_event, O.audit_timestamp,
        #              N.id, N.acst, N.audit_event, N.audit_timestamp,
        #              CR.cx_id, CR.re_api_id
        #              from cars_audit:prog_enr_rec N
        #              left join cars_audit:prog_enr_rec O
        #              on O.id = N.id
        #              and O.acst != N.acst
        #              and O.audit_event = 'BU'
        #              JOIN cvid_rec CR
        #              ON CR.cx_id = O.id
        #              where N.audit_event != 'BU'
        #              and N.audit_timestamp > TODAY - 1
        #              and N.audit_timestamp = O.audit_timestamp
        #              and CR.re_api_id is not null
        #     '''

        # for testing...

        statquery = '''select PER.id, PER.acst, 'BU', '', PER.id, PER.acst, 
            'AU', '', PER.id, CR.re_api_id
            from prog_enr_rec PER
            JOIN acad_stat_table AST
            on AST.acst = PER.acst
            JOIN cvid_rec CR on 
            CR.cx_id = PER.id
            where PER.id in (1387218)'''
        print(statquery)

        connection = get_connection(EARL)
        with connection:
            data_result = xsql(statquery, connection).fetchall()
            ret = list(data_result)
            for i in ret:
                print(str(i[0]) + " " + i[5] + " " + str(i[9]))
                carth_id = i[0]
                acad_stat = i[5]
                bb_id = i[9]
                print(bb_id)
                """
                   -----------------------------------------------------------
                  --2-FIND RAISERS EDGE ID IN LOCAL TABLE --------------------
                    MAY NOT BE NECESSARY IF I ASSUME ALL THE INDIVIDUALS
                    THAT MATTER ARE IN CVID_REC ALREADY AND DON"T LOOK FOR
                    CHANGES FOR ANY OTHER STUDENTS
                   -----------------------------------------------------------

                  Look for student and status in local table
                  Else look for student and status at BB via API
                  Add to BB if necessary (THIS WILL BE DONE BY OMATIC)
                  Add or update status in BB
                  Update local table if necessary
                """
                """1. Look for id in local table"""
                # # initialize bb_id
                # bb_id = 0
                # chk_sql = '''select re_api_id from cvid_rec
                #     where cx_id = {}'''.format(carth_id)
                # print(chk_sql)
                # connection = get_connection(EARL)
                # with connection:
                #     data_result = xsql(chk_sql, connection).fetchall()
                #     if data_result is None:
                #         print("Query cvid_rec:  No bb_id stored locally")
                #         pass
                #     else:
                #         ret = list(data_result)
                #         # if ret:
                #         for j in ret:
                #             if j[0] is not None:
                #                 bb_id = j[0]
                #                 print("BB ID = " + str(bb_id))
                #             else:
                #                 print("No bb_id stored locally")
                #                 bb_id = get_constituent_id(current_token, carth_id)
                #                 print(bb_id)
                #
                #         '''-------------------------------------------------------
                #           --3-UPDATE THE CUSTOM STUDENT STATUS FIELD----------------
                #         ----------------------------------------------------------
                #         '''
                if bb_id != 0:
                    print("Update custom field")
                    # Get the row id of the custom field record
                    field_id = get_const_custom_fields(current_token, bb_id,
                                                  'Student Status')

                    print("set custom fields: " + str(carth_id) + ", "
                          + acad_stat)

                    """ret is the id of the custom record, not the student"""
                    if field_id == 0:
                        print('Add new record?')
                    else:
                        print('Update record ' + str(field_id) + ' ' 
                              + acad_stat)
                        ret1 = update_const_custom_fields(current_token,
                                                      str(field_id),
                                                      'Test',
                                                      acad_stat)
                        print(ret1)
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
