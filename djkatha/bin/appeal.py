#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import datetime
import itertools
import logging
import os
import sys

# env
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djskeletor.settings.shell')

# required if using django models
import django
django.setup()

from django.conf import settings
from django.core.cache import cache
from djkatha.api.views import get_appeal
from djkatha.core.sky_api_calls import api_get


logger = logging.getLogger('debug_logfile')

# set up command-line options
desc = """
Accepts as input an appeal ID
"""

# RawTextHelpFormatter method allows for new lines in help text
parser = argparse.ArgumentParser(
    description=desc, formatter_class=argparse.RawTextHelpFormatter,
)

parser.add_argument(
    '-a',
    '--appeal',
    required=True,
    help="Appeal ID",
    dest='appeal',
)
parser.add_argument(
    '-d',
    '--display',
    required=True,
    help="Display type",
    dest='display',
)
parser.add_argument(
    '--test',
    action='store_true',
    help="Dry run?",
    dest='test',
)


def main():
    """Obtain appeal data from sky api."""
    donations = []
    constituents = []
    ticker = {}
    gifts = get_appeal(appeal)
    for gift in gifts['value']:
        post_date = datetime.datetime.strptime(gift['post_date'], '%Y-%m-%dT%H:%M:%S')
        if post_date > settings.GIVING_DAY_START_DATE:
            ticker[gift['id']] = gift
            donations.append(gift)

    if display == 'ticker':
        donations = reversed(sorted(ticker.keys()))

    for donation in donations:
        if test:
            print(donation, ticker[donation]['post_date'])

        if display == 'ticker':
            cid = ticker[donation]['constituent_id']
        else:
            cid = gift['constituent_id']

        cid = ticker[donation]['constituent_id']
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
        if constituent not in constituents and constituent.get('last'):
            constituents.append(constituent)
    if test:
        print(len(donations))
        print(len(constituents))
    else:
        for constituent in constituents[:30]:
            print(constituent['last'], constituent['first'])


if __name__ == '__main__':
    args = parser.parse_args()
    appeal = args.appeal
    display = args.display
    test = args.test

    if test:
        print(args)

    sys.exit(main())
