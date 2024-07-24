from django.urls import reverse

from axis.examine.machinery import PassiveMachinery
from axis.home.api import HomeViewSet
from axis.home.forms import HomeBLGCreationForm
from axis.home.models import Home

__author__ = "Artem Hruzd"
__date__ = "06-24-19 5:44 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


class HomeBLGCreationExamineMachinery(PassiveMachinery):
    """Create a home from a BLG Widget"""

    model = Home
    form_class = HomeBLGCreationForm
    type_name = "home_blg"
    api_provider = HomeViewSet

    form_template = "examine/home/blg_form.html"

    def _format_url_name(self, url_name, **kwargs):
        return url_name.format(model="home")

    def get_object_endpoint(self, instance):
        """Object Endpoint to hit up"""
        return reverse("apiv2:home-parse-blg")

    def get_edit_actions(self, instance):
        """No way to edit this it's one field"""
        return []
