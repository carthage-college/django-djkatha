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
import mysql.connector
import pyodbc


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


# def api_get(current_token, url):

def find_changes():
    try:
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

    except Exception as e:
    print("Error in main:  " + str(e))
    # fn_write_error("Error in misc_fees.py - Main: "
    #                + e.message)

def write_bb_id():
    try:
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

        """
            **************************************
            **************************************
            **************************************
        """

        """ --------GET THE BLACKBAUD CONSTITUENT ID-----------------"""
        """ I will either have a list of students in a csv file or possibly
            in  a to be determined database
            That way I can get the blackbaud internal id en masse and
            not need to make multiple calls based on the carthage ID
            I may also look to see if the student status has changed in 
            CX
        """

        # #----------------------------------------
        with open("id_list.csv", 'r') as id_lst:
            reed = csv.reader(id_lst, delimiter=',')
            for row in reed:
                # print(row)
                const_id = row[1]

        # # # First, we have to get the internal ID from blackbaud for
        # # the constituent
        # const_id = get_constituent_id(current_token, 1534657)
        print("Constituent id = " + str(const_id))

    except Exception as e:
        print("Error in main:  " + str(e))
        # fn_write_error("Error in misc_fees.py - Main: "
        #                + e.message)