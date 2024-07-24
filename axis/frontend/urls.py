"""views.py: Django core urls"""

from django.apps import apps
from django.conf import settings
from django.urls import re_path
from django.views.generic import RedirectView

from .views import FrontendView

__author__ = "Steven Klass"
__date__ = "2011/06/22 09:56:26"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = ["Steven Klass"]

app = apps.get_app_config("frontend")


# Map of url paths (without ^$) to url names for pass-through to angular
forward_urls = {
    r"/": "home",
    # flatpages
    r"news": "news",
    r"products": "products",
    r"pricing": "pricing",
    r"about": "about",
    r"contact": "contact",
    r"contact-success": "contact_success",
    # r'floorplan': 'floorplan:list',
    r"company/(?P<type>[^/]+)": "company-list",
    r"company/(?P<type>[^/]+)/add": "company-add",
    r"company/(?P<type>[^/]+)/(?P<pk>\d+)": "company-view",
}

urlpatterns = [
    # url(r'^{app.DEPLOY_URL}{pattern}$'.format(app=app, pattern=pattern),
    #     FrontendView.as_view(),
    #     name='frontend-{name}'.format(name=name))
    # for pattern, name in forward_urls.items()
]

if settings.DEBUG:
    urlpatterns += [
        re_path(
            r"^{app.DEPLOY_URL}assets/(?P<path>.*)$".format(app=app),
            RedirectView.as_view(url="http://{app.FRONTEND_HOST}assets/%(path)s".format(app=app)),
        ),
        re_path(
            r"^{app.DEPLOY_URL}(?P<path>.*-es\d+\.js.*)$".format(app=app),
            RedirectView.as_view(url="http://{app.FRONTEND_HOST}%(path)s".format(app=app)),
        ),
    ]

urlpatterns += [
    re_path(r"^{app.DEPLOY_URL}".format(app=app), FrontendView.as_view()),
]
