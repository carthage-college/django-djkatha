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
    1. Find relationships for all students who have a re_api_id in the cvid_rec
    table
    Insert or update accordingly
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
        # if database == 'sandbox':
        #     EARL = settings.INFORMIX_ODBC_SANDBOX

        else:
            # # this will raise an error when we call get_engine()
            # below but the argument parser should have taken
            # care of this scenario and we will never arrive here.
            EARL = None
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

        # for real..
        # Two options.  Get all changed records, look for local BB ID but ALSO
        # look for BB ID via API.  If there is a record in BB, then add the
        # BB ID locally if it doesn't exist.
        # OR
        # Ignore all changes locally that do not match an existing local BB ID
        # The latter would be the lowest hits on the API
        statquery = '''select c.id, rr.constituent_id, rr.reciprocal_id,
                rrt.value, rrt.code,
                rt.code, rt.value
                from constituent c
                join relationship_role rr
                on rr.constituent_id = c.id
                join relationship r
                on r.id = rr.relationship_id
                join relationship_role_type rrt
                on rrt.id= rr.reciprocal_type_id
                join relationship_type rt
                on rt.id =  rrt.relationship_type_id 
                where c.id in ( select DISTINCT CR.cx_id --, SAR.yr, SAR.sess, SAR.acst  
                from train:cvid_rec CR
                join stu_acad_rec SAR on SAR.id = CR.cx_id
                where CR.re_api_id is not null
                and SAR.yr = YEAR(TODAY)
                and SAR.ACST IN ('GOOD' ,'LOC' ,'PROB' ,'PROC' ,'PROR' ,'READ' ,'RP' ,
			    'SAB' ,'SHAC' ,'SHOC'))
            '''

        connection = get_connection(EARL)
        with connection:
            data_result = xsql(statquery, connection).fetchall()
            ret = list(data_result)
            for i in ret:
                print(str(i[0]) + " " + i[1])


                        '''-------------------------------------------------------
                          --3-UPDATE THE CUSTOM STUDENT STATUS 
                          FIELD----------------
                        ----------------------------------------------------------
                        '''
                        if bb_id != 0:
                            print("Update custom field")
                            # ret = get_const_custom_fields(current_token, bb_id,
                            #                               'Student Status')


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
