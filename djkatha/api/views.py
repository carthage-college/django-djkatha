# -*- coding: utf-8 -*-

"""URLs for all views."""

from django.conf import settings
from django.shortcuts import render


def callback(request):
    """Call back from raiser's edge API."""
    if request.method=='POST':
        response = request.POST
    else:
        response = request.GET
    return render(
        request, 'api/callback.html', {'response': response},
    )
