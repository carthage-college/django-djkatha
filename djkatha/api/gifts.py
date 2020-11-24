#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import sys

# env
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djkatha.settings.shell')

# required if using django models
import django
django.setup()

from django.conf import settings
from django.core.cache import cache
from djkatha.core.sky_api_auth import fn_do_token
from djkatha.core.sky_api_calls import api_get

# set up command-line options
desc = """
    Accepts as input an appeal ID.
"""

parser = argparse.ArgumentParser(
    description=desc, formatter_class=argparse.RawTextHelpFormatter,
)
parser.add_argument(
    '--appeal',
    required=True,
    help="Appeal ID",
    dest='appeal',
)
parser.add_argument(
    '--test',
    action='store_true',
    help="Dry run?",
    dest='test',
)


def main():
    """Obtain all the gifts for a specific appeal."""
    earl_appeal = '{0}/fundraising/v1/appeals/{1}'.format(
        settings.BB_SKY_API_URL,
        appeal,
    )
    key_campaign = 'campaigns_{0}'.format(appeal)
    earl_gift = '{0}/gift/v1/gifts?appeal_id={1}&limit=2500'.format(
        settings.BB_SKY_API_URL,
        appeal,
    )
    current_token = fn_do_token()
    campaign = cache.get(key_campaign)
    if not campaign:
        campaign = api_get(current_token, earl_appeal)
        cache.set(key_campaign, campaign)
    print(campaign)
    gifts = api_get(current_token, earl_gift)
    for gift in gifts['value']:
        cid = gift['constituent_id']
        key_constituent = 'constituents_{0}'.format(cid)
        constituent = cache.get(key_constituent)
        if not constituent:
            constituent = api_get(
                current_token,
                '{0}/constituent/v1/constituents/{1}'.format(
                    settings.BB_SKY_API_URL,
                    cid,
                )
            )
            cache.set(key_constituent, constituent)
        print(
            gift['amount']['value'],
            gift['is_anonymous'],
            gift.get('constituency'),
            gift['constituent_id'],
            constituent.get('last'),
            constituent.get('first'),
        )
    print('count = {0}'.format(gifts['count']))
    print('next_link = {0}'.format(gifts.get('next_link')))


if __name__ == '__main__':

    args = parser.parse_args()
    appeal = args.appeal
    test = args.test

    if test:
        print(args)

    sys.exit(main())
