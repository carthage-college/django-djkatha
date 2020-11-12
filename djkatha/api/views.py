# -*- coding: utf-8 -*-

"""URLs for all views."""

from django.conf import settings
from django.shortcuts import render


def call_back(request):
    """Call back from raiser's edge API."""
    return render(
        request, 'api/call_back.html', {'response': request.response},
    )
