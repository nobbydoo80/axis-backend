"""urls.py: Frontend delivery view"""


import logging

from django.apps import apps
from django.views.generic import TemplateView

__author__ = "Autumn Valenta"
__date__ = "2011/06/22 09:56:26"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = ["Autumn Valenta"]

log = logging.getLogger(__name__)
app = apps.get_app_config("frontend")


class FrontendView(TemplateView):
    template_name = "axis-frontend/index.html"

    def get_context_data(self, **kwargs):
        return super(FrontendView, self).get_context_data(
            FRONTEND_HOST=app.get_frontend_host(self.request), DEPLOY_URL=app.DEPLOY_URL, **kwargs
        )
