# -*- coding: utf-8 -*-

"""URLs for all views."""

import json
import requests

from django.conf import settings
from django.core.cache import cache
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render

from djkatha.core.sky_api_auth import fn_do_token
from djkatha.core.sky_api_calls import api_get


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


def donors(request, appeal):
    """Display donors for an appeal campaign."""
    earl_appeal = '{0}/fundraising/v1/appeals/{1}'.format(
        settings.BB_SKY_API_URL,
        appeal,
    )
    key_campaign = 'campaigns_{0}'.format(appeal)
    earl_gift = '{0}/gift/v1/gifts?appeal_id={1}&limit=2500'.format(
        settings.BB_SKY_API_URL,
        appeal,
    )
    donors = []
    current_token = fn_do_token()
    campaign = cache.get(key_campaign)
    if not campaign:
        campaign = api_get(current_token, earl_appeal)
        cache.set(key_campaign, campaign)
    # fetch the appeal campaign
    campaign = cache.get(key_campaign)
    if not campaign:
        campaign = api_get(current_token, earl_appeal)
        cache.set(key_campaign, campaign)
    # fetch all donations
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
        if constituent not in donors and constituent.get('last'):
            donors.append(constituent)

    return render(
        request, 'donors/index.html', {'donors': donors, 'count': len(donors)},
    )
