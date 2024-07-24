"""views.py: Django reso"""


import logging

from django.http import HttpResponse
from django.views.generic import View

from axis.core.mixins import AuthenticationMixin
from .RESO.data_models.reso import RESO1p4EDMX

__author__ = "Steven Klass"
__date__ = "07/23/17 09:15"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class EDMXView(View):
    def get(self, request, *args, **kwargs):
        reso = RESO1p4EDMX()
        return HttpResponse(reso.pprint(as_string=True), status=200, content_type="text/xml")
