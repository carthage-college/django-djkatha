
# from pathlib import Path
import requests
# import sys
import os
import json
import time
# import base64
import datetime
import django
import csv

from datetime import datetime
# Note to self, keep this here
# django settings for shell environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djequis.settings")
django.setup()
# ________________
from django.conf import settings
from django.core.cache import cache

def api_get(current_token, url):
    print("In api_get")
    try:

        params = {'HOST': 'api.sky.blackbaud.com'}
        status = 'Initial Value'
        # Setting status to something other than 200 initially
        while status != 200 or url != '':
            time.sleep(.2)  # SKY API Rate limited to 5 calls/sec

            headers = {'Bb-Api-Subscription-Key':
                           settings.BB_SKY_SUBSCRIPTION_KEY,
                       'Authorization': 'Bearer ' + current_token}

            response = requests.get(url=url,
                                    params=params,
                                    headers=headers)
            status = response.status_code
            # print(status)
            if status == 400:
                print('ERROR:  ' + str(status) + ":" + response.text)
                return 0

            elif status == 403:   # OUT OF API QUOTA - Quit
                print('ERROR:  ' + str(status) + ":" + response.text)
                print('You\'re out of API Quota!')
                return 0

            else:
                #     if response_dict['count'] == 0:
                response_dict = json.loads(response.text)
                return response_dict

    except Exception as e:
        print("Error in api_get:  " + e.message)
        # fn_write_error("Error in api_get - Main: "
        #                + e.message)
        return 0


def api_post(current_token, url, data):
    print("In api_post")
    try:
        params = {'HOST': 'api.sky.blackbaud.com'}
        # status = 'Initial Value'

        headers = {'Content-Type': 'application/json',
                   'Bb-Api-Subscription-Key': settings.BB_SKY_SUBSCRIPTION_KEY,
                   'Authorization': 'Bearer ' + current_token}

        response = requests.post(url=url, headers=headers,
                                params=params,
                                data=json.dumps(data)
                                )
        status = response.status_code
        stat_msg = response.text
        print(status)
        print(stat_msg)

        return status
    except Exception as e:
        print("Error in api_post:  " + e.message)
        # fn_write_error("Error in api_post.py - Main: "
        #                + e.message)
        return 0


def api_patch(current_token, url, data):
    print("In api_patch")
    try:
        params = {'HOST': 'api.sky.blackbaud.com'}
        # status = 'Initial Value'

        headers = {'Content-Type': 'application/json',
                   'Bb-Api-Subscription-Key': settings.BB_SKY_SUBSCRIPTION_KEY,
                   'Authorization': 'Bearer ' + current_token}

        response = requests.patch(url=url, headers=headers,
                                 params=params,
                                 data=json.dumps(data)
                                 )
        status = response.status_code
        stat_msg = response.text
        print(status)
        print(stat_msg)

        return status
    except Exception as e:
        print("Error in api_patch:  " + e.message)
        # fn_write_error("Error in api_patch.py - Main: "
        #                + e.message)
        return 0


def api_delete(current_token, url):
    print("In api_delete")
    try:
        params = {'HOST': 'api.sky.blackbaud.com'}

        headers = {'Content-Type': 'application/json',
                   'Bb-Api-Subscription-Key': settings.BB_SKY_SUBSCRIPTION_KEY,
                   'Authorization': 'Bearer ' + current_token}

        response = requests.delete(url=url, headers=headers, params=params)
        status = response.status_code
        stat_msg = response.text
        print(status)
        print(stat_msg)

        return status
    except Exception as e:
        print("Error in api_delete:  " + e.message)
        # fn_write_error("Error in api_delete.py - Main: "
        #                + e.message)
        return 0


def get_const_custom_fields(current_token, id, category):
    print("In get_const_custom_fields")
    try:
        urlst = 'https://api.sky.blackbaud.com/constituent/v1/constituents/' \
                + str(id) + '/customfields'
        x = api_get(current_token, urlst)
        # print(x)

        # This will return multiple records...How to parse things to get the
        # one item I want...
        if x == 0:
            print("NO DATA")
            return 0
        else:
            for i in x['value']:
                # print(i)
                if i['category'] == category:
                    item_id = i['id']
                    print("ID = " + i['id'])
                    print("Category = " + i['category'])
                    # if 'comment' not in x['value']:
                    #     print("Comment not entered")
                    # else:
                    #     print("Comment = " + str(i['comment']))
                    # print("Date = " + i['date'])
                    print("Date Added = " + i['date_added'])
                    print("Date Modified = " + i['date_modified'])
                    print("Parent id = " + i['parent_id'])
                    # print("Type = " + i['type'])
                    print("Value = " + i['value'])
                    return item_id

    except Exception as e:
        print("Error in get_const_custom_fields:  " + e.message)
        # fn_write_error("Error in misc_fees.py - Main: "
        #                + e.message)
        return 0


def get_relationships(current_token, id):
    urlst = 'https://api.sky.blackbaud.com/constituent/v1/constituents/' \
            + str(id) + '/relationships'
    try:

        x = api_get(current_token, urlst)
        if x == 0:
            print("NO DATA")
            return 0
        else:
            for i in x['value']:
                # print(i)
                print(i['relation_id'])
                print(i['type'])
                print(i['constituent_id'])
                print(i['relation_id'])
                print(i['reciprocal_type'])
                print(i['id'])
                print(i['date_modified'])
                print(i['is_organization_contact'])
                print(i['is_primary_business'])
                print(i['is_spouse'])
                # print(i['start'])
            return 1
    except Exception as e:
        print("Error in get_relationships:  " + e.message)
        # fn_write_error("Error in misc_fees.py - Main: "
        #                + e.message)
        return 0


def get_custom_fields(current_token):
    urlst = 'https://api.sky.blackbaud.com/constituent/v1/constituents/' \
            'customfields/categories/details'

    x = api_get(current_token, urlst)
    if x == 0:
        print("NO DATA")
        return 0
    else:
        for i in x['value']:
            # print(i)
            print(i['name'])
            print(i['type'])
        return 1


def get_custom_field_value(current_token, category):
    try:
        urlst = 'https://api.sky.blackbaud.com/constituent/v1/constituents/' \
                'customfields/categories/values?category_name=' + category
        # print(urlst)
        x = api_get(current_token, urlst)
        # print(x)
        if x == 0:
            print("NO DATA")
            return 0
        else:
            # for i in x['value']:
            print(x)
                # print(i)
            return 1
    except Exception as e:
        print("Error in get_custom_field_value:  " + e.message)
        # fn_write_error("Error in misc_fees.py - Main: "
        #                + e.message)
        return 0


def get_constituent_id(current_token, carthid):
    try:
        urlst =  'https://api.sky.blackbaud.com/constituent/v1/constituents/' \
                 'search?search_text=' + str(carthid) \
                 + '&search_field=lookup_id'

        x = api_get(current_token, urlst)
        if x == 0:
            print("NO DATA")
            return 0
        else:
            for i in x['value']:
            # print(x)
                print(i['id'])
                id = i['id']
                print(i['name'])
                print(i['lookup_id'])
                print(i['inactive'])

            return id

    except Exception as e:
        print("Error in get_constituent_id:  " + e.message)
        # fn_write_error("Error in get_constituent_id.py - Main: "
        #                + e.message)
        return 0


def get_constituent_list(current_token):
    try:

        urlst = 'https://api.sky.blackbaud.com/constituent/v1/constituents?' \
                'custom_field_category=Student Status' \
                '&date_added>2019-11-13T10:59:03.761-05:00&limit=10'
        # urlst =  'https://api.sky.blackbaud.com/constituent/v1/constituents/' \
        #          'search?search_text=' + str(carthid) \
        #          + '&search_field=lookup_id'

        x = api_get(current_token, urlst)
        if x == 0:
            print("NO DATA")
            return 0
        else:
            with open("id_list.csv", 'w') as id_lst:
                for i in x['value']:
                # print(x)
                #     print(i['id'])
                    bb_id = i['id']
                    carth_id = i['lookup_id']
                    name = i['name']
                    type = i['type']
                    if type == 'Individual':
                        # print('Name = ' + name + ', CarthID = ' + str(carth_id)
                        #   + ', BlackbaudID = ' + str(bb_id) + ', type = '
                        #   + type)
                        csvwriter = csv.writer(id_lst, quoting=csv.QUOTE_NONE)
                        csvwriter.writerow([carth_id, bb_id, name, type])
            return 1

    except Exception as e:
        print("Error in get_constituent_id:  " + e.message)
        # fn_write_error("Error in get_constituent_id.py - Main: "
        #                + e.message)
        return 0

def delete_const_custom_fields(current_token, itemid):
    try:
        urlst = 'https://api.sky.blackbaud.com/constituent/v1/constituents/' \
                'customfields/' + str(itemid)

        print(urlst)
        x = api_delete(current_token, urlst)
        if x == 0:
            print("Delete Failure")
            return 1
        else:
            return 0

    except Exception as e:
        print("Error in delete_const_custom_fields:  " + e.message)
        # fn_write_error("Error in delete_const_custom_fields ")
        #                + e.message)
        return 0


def update_const_custom_fields(current_token, itemid, comment, val):
    try:
        print(itemid)
        urlst = 'https://api.sky.blackbaud.com/constituent/v1/constituents/' \
                'customfields/' + itemid

        now = datetime.now()
        date_time = now.strftime("%Y-%m-%dT%H:%M:%S")

        body = {"comment": comment, "date_modified": "2019-11-13T01:25:00",
                "date": "2019-11-12T01:25:00", "value": val}

        print(urlst, body)
        x = api_patch(current_token, urlst, body)
        if x == 0:
            print("Patch Failure")
            return 1
        else:
            return 0


    except Exception as e:
        print("Error in update_const_custom_fields:  " + e.message)
        # fn_write_error("Error in update_const_custom_fields ")
        #                + e.message)
        return 0


def set_const_custom_field(current_token, id, value, category, comment):
    # Not passing an item id - this is a create, one will be created
    urlst = 'https://api.sky.blackbaud.com/constituent/v1/constituents/' \
            'customfields'

    now = datetime.now()
    date_time = now.strftime("%Y-%m-%dT%H:%M:%S")

    # Constituent ID is passed in as Parent ID
    body = {'category': category, 'comment': comment, 'date': date_time,
            'parent_id': id, 'value': value}

    print(urlst, body)

    x = api_post(current_token, urlst, body)
    if x == 0:
        print("Post Failure")
        return 0
    else:
        return 1


