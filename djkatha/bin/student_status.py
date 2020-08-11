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
import datetime
from datetime import date, timedelta, datetime
import time
from time import strftime

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
import sky_constituent_list
from django.conf import settings
from django.core.cache import cache
from djkatha.core.utilities import fn_write_error, fn_send_mail
from djkatha.core.sky_api_auth import fn_do_token
from djkatha.core.sky_api_calls import api_get, get_const_custom_fields, \
    get_constituent_id, set_const_custom_field, update_const_custom_fields, \
    delete_const_custom_fields, get_relationships, api_post, api_patch, \
    api_delete, get_custom_fields, get_custom_field_value, \
    get_constituent_list

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

def main():
    try:

        # set global variable
        global EARL

        datetimestr = time.strftime("%Y%m%d%H%M%S")
        # Defines file names and directory location
        RE_STU_LOG = settings.BB_LOG_FOLDER + 'RE_student_status' \
                     + datetimestr + ".txt"
        # print(RE_STU_LOG)

        # determines which database is being called from the command line
        if database == 'cars':
            EARL = settings.INFORMIX_ODBC
        elif database == 'train':
            EARL = settings.INFORMIX_ODBC_TRAIN

        """"--------GET THE TOKEN------------------"""
        current_token = fn_do_token()

        """
            -----------------------------------------------------------
            Debating whether to call the sky_constituent_list routine here
            to make sure the cvid_rec entries are current
            -----------------------------------------------------------
        """
        # os.system("python sky_constituent_list.py --database=cars")

        # Probably should change the other file to a class or whatever if I
        # do this permanently
        # sky_constituent_list.main()

        """
           -----------------------------------------------------------
           -1-GET STUDENTS WITH A STATUS CHANGE FROM PROG_ENR_REC-----
            Assume all current blackbaud students have a re_api_id in the 
            cvid_rec table.  This will be handled through a separate prior
            process.
            Look for status changes only for students who have the 
            re_api_id entry
           -----------------------------------------------------------
        """

        """THis query looks for recent changes in the student status.  
            We do not want to use any records that do NOT have an re_api_id 
           value.  It only applies to RE entered students at present"""

        """To get the last query date from cache"""
        last_sql_date = cache.get('Sql_date')
        # print(last_sql_date)

        statquery = '''
            select O.id, O.acst, O.audit_event, TO_CHAR(O.audit_timestamp),
                N.id, N.acst, N.audit_event, N.audit_timestamp,
                CR.cx_id, CR.re_api_id, max(N.audit_timestamp)
                from cars_audit:prog_enr_rec N
                left join cars_audit:prog_enr_rec O
                on O.id = N.id
                and O.acst != N.acst
                and O.audit_event in ('BU', 'I')
            left JOIN cvid_rec CR
                ON CR.cx_id = O.id
            where
                (N.audit_event != 'BU'
                and N.audit_timestamp = O.audit_timestamp)
                and N.audit_timestamp >= "{0}"
                and CR.re_api_id is not null
                --and N.id = 1468587
            group by O.id, O.acst, O.audit_event, O.audit_timestamp,
                N.id, N.acst, N.audit_event, N.audit_timestamp,
                CR.cx_id, CR.re_api_id

            UNION

            select id, '' acst, '' audit_event, '' audit_timestamp,
                N.id, N.acst, N.audit_event, N.audit_timestamp,
                CR.cx_id, CR.re_api_id, max(N.audit_timestamp)
                from cars_audit:prog_enr_rec N

            left JOIN cvid_rec CR
                ON CR.cx_id = N.id
            where
                (N.audit_event = 'I')
                and N.audit_timestamp >=  "{0}"
                and (CR.re_api_id is not null)
                --and N.id = 1468649
            group by id, acst, audit_event, audit_timestamp,
                N.id, N.acst, N.audit_event, N.audit_timestamp,
                CR.cx_id, CR.re_api_id;
            '''.format(last_sql_date)


        connection = get_connection(EARL)
        with connection:
            data_result = xsql(statquery, connection).fetchall()
            ret = list(data_result)
            if ret:
                for i in ret:
                    # print(str(i[8]) + " " + i[5] + " " + str(i[9]))
                    carth_id = i[8]
                    acad_stat = i[5]
                    bb_id = i[9]
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
                    #         '''------------------------------------------------
                    #           --3-UPDATE THE CUSTOM STUDENT STATUS FIELD-------
                    #         ---------------------------------------------------
                    #         '''
                    if bb_id != 0:
                        # Get the row id of the custom field record
                        field_id = get_const_custom_fields(current_token, bb_id,
                                                      'Student Status')
                        # print("set custom fields: " + str(carth_id) + ", "
                        #            + acad_stat)

                        """ret is the id of the custom record, not the student"""
                        if field_id == 0:
                            # print("Error in student_status.py - for: "
                            #                + str(carth_id) + ", Unable to get
                            #                the custom field")
                            fn_write_error("Error in student_status.py - for: "
                                       + str(carth_id) + ", Unable to get the "
                                       "custom field")
                            fn_send_mail(settings.BB_SKY_TO_EMAIL,
                                settings.BB_SKY_FROM_EMAIL, "SKY API ERROR",
                                    "Error in student_status.py - for: "
                                         + str(carth_id)
                                         + ", Unable to get the custom field")
                            pass
                        else:
                            ret1 = update_const_custom_fields(current_token,
                                                          str(field_id),
                                                          'CX Status Update',
                                                          acad_stat)

                            if ret1 == 0:
                                # print("set custom fields: " + str(carth_id)
                                # + ", " + acad_stat)
                                f = open(RE_STU_LOG, "a")
                                f.write("set custom fields: " + str(carth_id)
                                        + ", " + acad_stat + '\n')
                                f.close()
                            else:
                                print("Patch failed")

                    else:
                        print("Nobody home")
                        pass
                print("Process complete")
                fn_send_mail(settings.BB_SKY_TO_EMAIL,
                             settings.BB_SKY_FROM_EMAIL, "SKY API",
                             "New records processed for Blackbaud: ")

            else:
                 print("No changes found")
                 fn_send_mail(settings.BB_SKY_TO_EMAIL,
                             settings.BB_SKY_FROM_EMAIL, "SKY API",
                             "No new records for Blackbaud: ")

        """To set a new date in cache"""
        a = datetime.now()
        last_sql_date = a.strftime('%Y-%m-%d %H:%M:%S')
        cache.set('Sql_date', last_sql_date)
    
    except Exception as e:
        print("Error in main:  " + str(e))
        fn_write_error("Error in student_status.py - Main: "
                       + repr(e))
        fn_send_mail(settings.BB_SKY_TO_EMAIL,
                     settings.BB_SKY_FROM_EMAIL, "SKY API ERROR", "Error in "
                                "student_status.py - for: " + + repr(e))


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
