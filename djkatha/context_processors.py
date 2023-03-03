# -*- coding: utf-8 -*-

from django.conf import settings
from djtools.fields import TODAY


def sitevars(request):
    """Expose some settings to the template level."""
    context = {}
    context['year'] = TODAY.year
    context['managers'] = settings.MANAGERS_GROUP

    return context
