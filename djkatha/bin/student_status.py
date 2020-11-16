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
from datetime import datetime
import time

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

# import sky_constituent_list
from django.conf import settings
from django.core.cache import cache
from djimix.core.utils import get_connection
from djimix.core.utils import xsql
from djkatha.core.utilities import fn_send_mail
from djkatha.core.utilities import fn_write_error
from djkatha.core.sky_api_auth import fn_do_token
from djkatha.core.sky_api_calls import get_const_custom_fields
from djkatha.core.sky_api_calls import update_const_custom_fields
from sky_constituent_list import check_for_constituents

# normally set as 'debug" in SETTINGS
DEBUG = settings.INFORMIX_DEBUG
desc = """
    Collect data from Blackbaud
"""
parser = argparse.ArgumentParser(description=desc)

parser.add_argument(
    '--test',
    action='store_true',
    help="Dry run?",
    dest='test',
)
parser.add_argument(
    '-d',
    '--database',
    help="database name.",
    dest='database',
)


def main():
    try:
        # set global variable
        global EARL

        # determines which database is being called from the command line
        if database == 'cars':
            EARL = settings.INFORMIX_ODBC
        elif database == 'train':
            EARL = settings.INFORMIX_ODBC_TRAIN

        # To get the last query date from cache
        last_sql_date = cache.get('Sql_date')
        if not last_sql_date:
           # set a new date in cache
            a = datetime.now()
            last_sql_date = a.strftime('%Y-%m-%d %H:%M:%S')
            cache.set('Sql_date', last_sql_date)

        # This calls sky_constituent list to grab any recently added IDs
        check_for_constituents(EARL)

        # print('student status 1')
        datetimestr = time.strftime('%Y%m%d%H%M%S')
        # Defines file names and directory location
        RE_STU_LOG = settings.BB_LOG_FOLDER + 'RE_student_status' \
                     + datetimestr + ".txt"

        """"--------GET THE TOKEN------------------"""
        current_token = fn_do_token()

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

        # print(statquery)
        with get_connection(EARL) as connection:
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
                    -----------------------------------------------------------
                    Look for student and status in local table
                    Else look for student and status at BB via API
                    Add to BB if necessary (THIS WILL BE DONE BY OMATIC)
                    Add or update status in BB
                    Update local table if necessary
                    """

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
                                fn_write_error(
                                    "Error in student_status.py - Main:  "
                                    "Patch API call failed "
                                    + repr(e))
                                fn_send_mail(settings.BB_SKY_TO_EMAIL,
                                             settings.BB_SKY_FROM_EMAIL,
                                             "SKY API ERROR", "Error in "
                                             "student_status.py - for: "
                                             "Patch API call failed "
                                             + repr(
                                        e))
                                pass

                    else:
                        # print("Nobody home")
                        pass
                print("Process complete")
                fn_send_mail(
                    settings.BB_SKY_TO_EMAIL,
                    settings.BB_SKY_FROM_EMAIL,
                    "SKY API:  Last run was: {0}".format(str(last_sql_date)),
                    "New records processed for Blackbaud.",
                )

            else:
                # print("No changes found")
                fn_send_mail(
                    settings.BB_SKY_TO_EMAIL,
                    settings.BB_SKY_FROM_EMAIL,
                    "SKY API:  Last run was: {0}".format(str(last_sql_date)),
                    "No new records for Blackbaud.",
                )
                # print(last_sql_date)

    except Exception as e:
        print("Error in main: {0}".format(repr(e)))
        fn_write_error("Error in student_status.py - Main: %s" % repr(e))
        fn_send_mail(
            settings.BB_SKY_TO_EMAIL,
            settings.BB_SKY_FROM_EMAIL,
            "Error in student_status.py - for: {0}".format(repr(e)),
            "SKY API ERROR",
        )


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
        test = 'test'

    sys.exit(main())
