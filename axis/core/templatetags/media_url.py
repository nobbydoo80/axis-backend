"""media_url.py: Django core"""
import datetime
import logging

import dateutil.parser

from django import template
from django.template.defaultfilters import stringfilter

__author__ = "Steven Klass"
__date__ = "9/20/11 1:43 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = ["Steven Klass"]


log = logging.getLogger(__name__)
register = template.Library()


@register.filter
@stringfilter
def media_url(value, STATIC_URL):
    """Searches for {{ STATIC_URL }} and replaces it with the current STATIC_URL"""
    return value.replace("{{ STATIC_URL }}", STATIC_URL)


media_url.is_safe = True


@register.filter
@stringfilter
def site_url(value, site):
    """Searches for {{ STATIC_URL }} and replaces it with the current STATIC_URL"""
    return value.replace("{{ site }}", site.get_)


site_url.is_safe = True


@register.filter
@stringfilter
def date_from_url(url):
    """Searches for {{ STATIC_URL }} and replaces it with the current STATIC_URL"""
    date_obj = dateutil.parser.parse(url.split("/")[2]).replace(tzinfo=datetime.timezone.utc)
    return date_obj.strftime("%a %B %-d, %Y")


date_from_url.is_safe = True
