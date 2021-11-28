
# from pathlib import Path
import requests
# import sys
import os
import json
import time
import datetime
import csv
import arrow
import traceback

from djkatha.core.utilities import fn_send_mail
from djkatha.core.utilities import fn_write_error

from django.conf import settings


def api_get(current_token, url):
    # print("In api_get")
    # print(url)

    try:
        params = {'HOST': 'api.sky.blackbaud.com'}
        status = 0
        # Setting status to something other than 200 initially
        # print(status)
        while status != 200 or url != '':
            time.sleep(.2)  # SKY API Rate limited to 5 calls/sec
            headers = {'Bb-Api-Subscription-Key':
                           settings.BB_SKY_SUBSCRIPTION_KEY,
                       'Authorization': 'Bearer ' + current_token}
            # print(headers)
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
                # if response_dict['count'] == 0:
                #     return 0
                # else:
                return response_dict

    except Exception as e:
        print("Error in api_get:  " + str(e))
        fn_write_error("Error in sky_api_calls.py api_get: "
                       + str(e))
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
        # print(status)
        # print(stat_msg)

        return status
    except Exception as e:
        print("Error in api_post:  " + str(e))

        fn_write_error("Error in sky_api_calls.py api_post: "
                       + str(e))

        return 0


def api_patch(current_token, url, data):
    # print("In api_patch")
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
        # print(status)
        # print(stat_msg)

        return status
    except Exception as e:
        print("Error in api_patch:  " + str(e))
        fn_write_error("Error in sky_api_calls.py api_patch: "
                       + str(e))
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
        # print(status)
        # print(stat_msg)

        return status
    except Exception as e:
        print("Error in api_delete:  " + str(e))
        fn_write_error("Error in sky_api_calls.py api_delete: "
                       + str(e))
        return 0


def get_const_custom_fields(current_token, id, category):
    # print("In get_const_custom_fields")
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
                    # print("ID = " + i['id'])
                    # print("Category = " + i['category'])
                    # if 'comment' not in x['value']:
                    #     print("Comment not entered")
                    # else:
                    #     print("Comment = " + str(i['comment']))
                    # print("Date = " + i['date'])
                    # print("Date Added = " + i['date_added'])
                    # print("Date Modified = " + i['date_modified'])
                    # print("Parent id = " + i['parent_id'])
                    # print("Type = " + i['type'])
                    # print("Blackbaud Status Value = " + i['value'])
                    return item_id

    except Exception as e:
        print("Error in sky_api_calls.py - get_const_custom_fields "
                       "for: " + str(id) + ", " + str(e))
        fn_write_error("Error in sky_api_calls.py - get_const_custom_fields "
                       "for: " + str(id) + ", " + str(e))

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
        print("Error in get_relationships:  " + str(e))
        fn_write_error("Error in sky_api_calls.py - get_relationships: "
                       + str(e))
        return 0


def get_relationship_types(current_token):
    urlst = 'https://api.sky.blackbaud.com/constituent/v1/relationshiptypes'

    try:
        x = api_get(current_token, urlst)
        if x == 0:
            print("NO DATA")
            return 0
        else:
            for i in x['value']:
                print(i)
            return 1

    except Exception as e:
        print("Error in get_relationships:  " + str(e))
        fn_write_error("Error in sky_api_calls.py - get_relationship_types: "
                       + str(e))
        return 0



def get_custom_fields(current_token):
    # print("In get_custom_fields")
    urlst = 'https://api.sky.blackbaud.com/constituent/v1/constituents/' \
            'customfields/categories/details'

    x = api_get(current_token, urlst)
    if x == 0:
        print("NO DATA")
        return 0
    else:
        # for i in x['value']:
            # print(i)
            # print(i['name'])
            # print(i['type'])
        return 1


def get_constituents_custom_field_list(current_token, searchtime):

    a = datetime.datetime.strptime(str(searchtime), '%Y-%m-%d %H:%M:%S')
    # print(a)
    x = a.isoformat()
    # print(x)
    t = str(x)
    # print(t)
    z = x[:10] + 'T12:00:00.000-04:00'
    # z = t[:20] + '.0000000-04:00'
    # print(z)

    # 2020-01-05T12:00:00.0000000-04:00 THis works!
    """This calls the API Constituent Custom Field List (All Constituents)
        Uses the date added as a search param, as well as the custom field
        for student status.  Can be limited to a particular number of records.
        Offset param will skip the first N number of records
        Date added must be in format 2020-01-05T12:00:00.0000000-04:00"""
    urlst = "https://api.sky.blackbaud.com/constituent/v1/constituents/" \
            "customfields?date_added=" + searchtime + "" \
            "&category=Student Status" \
            "&limit=1500&"
    # urlst = "https://api.sky.blackbaud.com/constituent/v1/constituents/" \
    #         "customfields?category=Student Status&value=Blank"
    try:
        # print(urlst)
        x = api_get(current_token, urlst)
        return x
        # if x == 0:
        #     print("NO DATA")
        #     return 0
        # else:
        #     for i in x['value']:
        #         # print(i)
        #         print(i['parent_id'])
        #         print(i['value'])
        #     return 1
    except Exception as e:
        print("Error in get_relationships:  " + str(e))
        fn_write_error("Error in sky_api_calls.py - "
                       "get_constituents_custom_field_list: " + str(e))
        return 0



def get_custom_field_value(current_token, category):
    try:
        print("In get_custom_field_value")
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
            # print(x)
                # print(i)
            return 1
    except Exception as e:
        print("Error in get_custom_field_value:  " + str(e))
        fn_write_error("Error in sky_api_calls.py - "
                       "get_custom_field_value: " + str(e))
        return 0


def get_constituent_id(current_token, carthid):
    try:
        urlst =  'https://api.sky.blackbaud.com/constituent/v1/constituents/' \
                 'search?search_text=' + str(carthid) \
                 + '&search_field=lookup_id'

        x = api_get(current_token, urlst)
        if x == 0:
            # print("NO DATA")
            return 0
        else:
            for i in x['value']:
                # print(i['id'])
                id = i['id']
                # print(i['name'])
                # print(i['lookup_id'])
                # print(i['inactive'])

            return id

    except Exception as e:
        print("Error in get_constituent_id:  " + str(e))
        fn_write_error("Error in sky_api_calls.py - "
                       "get_constituent_id: " + str(e))
        return 0


def get_lookup_id(current_token, bb_id):
    try:
        urlst = 'https://api.sky.blackbaud.com/constituent/v1/constituents/' \
                 + str(bb_id)
        # print(urlst)

        x = api_get(current_token, urlst)
        if x == 0:
            # print("NO DATA")
            return 0
        else:
            # print(x)
            # print(x['lookup_id'])
            return x['lookup_id']

    except Exception as e:
        print("Error in get_lookup_id:  " + str(e))
        fn_write_error("Error in sky_api_calls.py - "
                       "get_lookup_id: " + str(e))
        return 0


def get_constituent_custom_fields(current_token, bb_id):
    urlst = 'https://api.sky.blackbaud.com/constituent/v1/constituents/' \
            + bb_id + '/customfields'
    try:
        print("In get_constituent_custom_fields")
        x = api_get(current_token, urlst)
        if x == 0:
            print("NO DATA")
            return 0
        else:
            # with open("id_list.csv", 'w') as id_lst:
            #     for i in x['value']:
            # print(x)
            #     #     print(i['id'])
            #         bb_id = i['id']
            #         carth_id = i['lookup_id']
            #         name = i['name']
            #         type = i['type']
            #         if type == 'Individual':
            #             # print('Name = ' + name + ', CarthID = ' + str(carth_id)
            #             #   + ', BlackbaudID = ' + str(bb_id) + ', type = '
            #             #   + type)
            #             csvwriter = csv.writer(id_lst, quoting=csv.QUOTE_NONE)
            #             csvwriter.writerow([carth_id, bb_id, name, type])
            # return 1
            return x
    except Exception as e:
        print("Error in get_constituent_id:  " + str(e))
        fn_write_error("Error in sky_api_calls.py - "
                       "get_constituent_custom_fields: " + str(e))
        return 0


def get_constituent_list(current_token, searchtime):

    try:
        print("In get_constituent_list")
        a = datetime.strptime(str(searchtime), '%Y-%m-%d')
        # print(a)
        x = a.isoformat()
        # print(x)
        t = str(x)
        # print(t)
        z = x[:10] + 'T12:00:00.000-04:00'
        # z = t[:20] + '.0000000-04:00'
        # print(z)

        # urlst = 'https://api.sky.blackbaud.com/constituent/v1/constituents?' \
        #             'custom_field_category=Student Status' \
        #         '&date_added>2019-11-13T10:59:03.761-05:00&limit=3'
        # print(urlst)

        # 2020-01-01T17:59:31.1600745-04:00  THis works
        # 2020-01-05T12:00:00.000-04:00 this fails
        # 2020-01-05T12:00:00.0000000-04:00 THis works!

        urlst = 'https://api.sky.blackbaud.com/constituent/v1/constituents?' \
                'custom_field_category=Student Status' \
                '&date_added>' + str(z) + '&limit=3'
        # print(urlst)

        # Student Status, Involvement
        x = api_get(current_token, urlst)
        # x = 0
        if x == 0:
            print("NO DATA")
            return 0
        else:
            #     for i in x['value']:
            #     # print(x)
            #     #     print(i['id'])
            #         bb_id = i['id']
            #         carth_id = i['lookup_id']
            #         name = i['name']
            #         type = i['type']
            #         if type == 'Individual':
            #             # print('Name = ' + name + ', CarthID = ' + str(carth_id)
            #             #   + ', BlackbaudID = ' + str(bb_id) + ', type = '
            #             #   + type)
            # return 1
            return x
    except Exception as e:
        print("Error in get_constituent_id:  " + str(e))
        fn_write_error("Error in sky_api_calls.py - "
                       "get_constituent_list: " + str(e))
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
        print("Error in delete_const_custom_fields:  " + str(e))
        fn_write_error("Error in sky_api_calls.py - "
                       "delete_const_custom_fields: " + str(e))
        return 0


def update_const_custom_fields(current_token, itemid, comment, val):
    try:
        # print("In update_const_custom_fields")
        # print(itemid)
        urlst = 'https://api.sky.blackbaud.com/constituent/v1/constituents/' \
                'customfields/' + itemid

        # now = datetime.now()
        # date_time = now.strftime("%Y-%m-%dT%H:%M:%S")

        utc = arrow.utcnow()
        # print(utc.to('US/Eastern'))
        date_time = utc.to('US/Eastern')
        # print(str(date_time))
        dat = str(date_time)

        body = {"comment": comment, "date_modified": dat,
                "date": dat, "value": val}

        # print(urlst, body)
        x = api_patch(current_token, urlst, body)
        if x == 0:
            print("Patch Failure")
            return 1
        else:
            # print("Patch Success")
            return 0


    except Exception as error:
        print("Error in update_const_custom_fields:  " + str(error))
        stack = traceback.print_exc()
        print(stack)
        fn_write_error("Error in sky_api_calls.py - "
                       "update_const_custom_fields: " + str(error))
        fn_write_error(stack)
        return 0


def set_const_custom_field(current_token, id, value, category, comment):
    # Not passing an item id - this is a create, one will be created
    print("In set_const_custom_field")
    urlst = 'https://api.sky.blackbaud.com/constituent/v1/constituents/' \
            'customfields'
    try:
        # now = datetime.now()
        # date_time = now.strftime("%Y-%m-%dT%H:%M:%S")

        utc = arrow.utcnow()
        # print(utc.to('US/Eastern'))
        date_time = utc.to('US/Eastern')

        # Constituent ID is passed in as Parent ID
        body = {'category': category, 'comment': comment, 'date': date_time,
                'parent_id': id, 'value': value}

        # print(urlst, body)

        # x = api_post(current_token, urlst, body)
        # if x == 0:
        #     print("Post Failure")
        #     return 0
        # else:
        #     return 1
    except Exception as e:
        print("Error in update_const_custom_fields:  " + str(e))
        fn_write_error("Error in sky_api_calls.py - "
                       "set_const_custom_field: " + str(e))
        return 0

