# -*- coding: utf-8 -*-

"""URLs for all views."""

import datetime
import json
import requests

from django.conf import settings
from django.core.cache import cache
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from djkatha.core.sky_api_auth import fn_do_token
from djkatha.core.sky_api_calls import api_get


def get_appeal(appeal):
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
    # fetch the appeal campaign
    campaign = cache.get(key_campaign)
    if not campaign:
        campaign = api_get(current_token, earl_appeal)
        cache.set(key_campaign, campaign)
    # fetch all donations
    return api_get(current_token, earl_gift)


def callback(request):
    """Call back from raiser's edge API."""
    if request.method=='POST':
        response = request.POST
    else:
        response = request.GET
    return render(
        request, 'api/callback.html', {'response': response},
    )


def token(request):
    """Authenticate and generate an OAUTH2 token to the SKY API."""
    code = request.GET.get('code')
    earl = 'https://{0}{1}'.format(settings.SERVER_URL, reverse('token'))
    if code:
        ref_token_getter = requests.post(
            url=settings.BB_SKY_TOKEN_URL,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            data={
                'grant_type': 'authorization_code',
                'code': code,
                'client_id': settings.BB_SKY_CLIENT_ID,
                'client_secret': settings.BB_SKY_CLIENT_SECRET,
                'redirect_uri': earl,
            },
        )
        tokens_dict = dict(json.loads(ref_token_getter.text))
        cache.set(
            settings.BB_SKY_TOKEN_CACHE_KEY, tokens_dict['access_token'],
        )
        cache.set(
            settings.BB_SKY_REFRESH_TOKEN_CACHE_KEY,
            tokens_dict['refresh_token'],
        )
        response = render(
            request, 'api/callback.html', {'response': code},
        )
    else:
        response = HttpResponseRedirect(
            '{0}{1}{2}{3}{4}'.format(
                settings.BB_SKY_AUTHORIZE_URL,
                '?response_type=code&client_id=',
                settings.BB_SKY_CLIENT_ID,
                '&redirect_uri=',
                earl,
            ),
        )
    return response


def donors(request, appeal, display):
    """Display donors for an appeal where display = list, ticker, mini."""
    donations = []
    constituents = []
    mini = []
    ticker = {}
    total = float()
    goal = float(settings.GIVING_DAY_GOALS[appeal]['goal'])
    earl = settings.GIVING_DAY_GOALS[appeal]['earl']
    percent = 0
    gifts = get_appeal(appeal)
    post_date = None
    if gifts and gifts.get('value'):
        for gift in gifts['value']:
            post_date = datetime.datetime.strptime(gift['post_date'], '%Y-%m-%dT%H:%M:%S')
            if post_date > settings.GIVING_DAY_START_DATE:
                ticker[gift['id']] = gift
                donations.append(gift)

    if display == 'ticker':
        donations = reversed(sorted(ticker.keys()))

    for donation in donations:
        if display == 'ticker':
            cid = ticker[donation]['constituent_id']
        else:
            cid = donation['constituent_id']
            amount = donation['amount']['value']
            total += amount

        key_constituent = 'constituents_{0}'.format(cid)
        constituent = cache.get(key_constituent)
        if not constituent:
            current_token = fn_do_token()
            constituent = api_get(
                current_token,
                '{0}/constituent/v1/constituents/{1}'.format(
                    settings.BB_SKY_API_URL,
                    cid,
                )
            )
            cache.set(key_constituent, constituent)
        if constituent not in mini:
            mini.append(constituent)
        if constituent not in constituents and constituent.get('last'):
            constituents.append(constituent)

    template = 'donors/{0}.html'.format(display)
    content_type='text/html; charset=utf-8'
    if display == 'ticker':
        content_type='text/plain; charset=utf-8'
        constituents = constituents[:settings.GIVING_DAY_TICKER_LIMIT]
    elif display == 'mini':
        constituents = mini
    percent = round(int((total / goal) * 100), 2)
    return render(
        request,
        template,
        {
            'count': len(constituents),
            'donors': constituents,
            'earl': earl,
            'percent': percent,
            'post_date': post_date,
            'total': '%.2f' % total,

        },
        content_type=content_type,
    )


def promotion_ajax(request, slug):
    """
    ajax request, returns HTML for dynamic display.
    accepts a campaign slug for identifying the Promotion() class object.
    """
    return render(
        request,
        'giving/promotion_ajax.html',
        {'data': None, 'earl': None},
    )
