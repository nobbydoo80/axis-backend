"""tags.py: Django core template tags"""


import logging
import re
from django import template
from django.urls import reverse
from django.conf import settings
from django.utils.timezone import now
from django.contrib.sites.models import Site

__author__ = "Steven Klass"
__date__ = "2011/06/22 09:56:26"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = ["Steven Klass"]

log = logging.getLogger(__name__)
register = template.Library()


@register.simple_tag
def active(request, urls):
    """Determines whether the url you have is active or not"""
    if not isinstance(request, str):
        if request.path in (reverse(url) for url in urls.split()):
            return "active"
    return ""


class ShowGoogleAnalyticsJS(template.Node):
    """Show the Google Analytics"""

    def render(self, context):
        """Render the Google Analytics"""
        if settings.DEBUG:
            return "<!-- Google Universal Analytics not included because you are in Debug mode! -->"

        code = getattr(settings, "GOOGLE_ANALYTICS_CODE", False)

        if not code:
            return (
                "<!-- Google Universal Analytics not included because you haven't set the "
                "settings.GOOGLE_ANALYTICS_CODE variable! -->"
            )

        user, company, company_type = None, None, None

        try:
            user = context["user"]
        except KeyError:
            try:
                user = context.get("request").user
            except AttributeError:
                pass

        if hasattr(user, "is_staff") and user.is_staff:
            return "<!-- Google Universal Analytics not included because you are a staff user! -->"

        try:
            company = context["company"]
            company_type = company.company_type
        except KeyError:
            try:
                company = context.get("request").company
                company_type = company.company_type
            except AttributeError:
                pass

        company_name = None
        if company:
            try:
                company_name = re.sub(r"'", "\\'", company.name)
            except (AttributeError, TypeError):
                pass

        try:
            site = context.get("site").domain
        except AttributeError:
            try:
                site = Site.objects.get_current().domain
            except Exception as err:
                log.exception("Unable to get site!")
                site = Site.objects.first().domain

        dts = now().strftime("%c")

        data = (
            """
            <script>
              (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
              (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
              m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
              })(window,document,'script','//www.google-analytics.com/analytics.js','ga');
              ga('create', '"""
            + code
            + """', '"""
            + site
            + """', { cookieDomain: '"""
            + site
            + """' });
              ga('require', 'displayfeatures');"""
        )
        if company_name:
            data += "\n              ga('set', 'dimension1', '{company}');".format(
                company=company_name
            )
        if user.id:
            data += "\n              ga('set', 'dimension2', '{user}');".format(user=user)
        if company_type:
            data += "\n              ga('set', 'dimension3', '{company_type}');".format(
                company_type=company_type
            )
        data += """\n              ga('send', 'pageview');
            </script>"""
        data += "<!-- {user} ({company}) {site} {dts} -->".format(
            user=user, company=company.name, site=site, dts=dts
        )
        return data


def googleanalyticsjs(parser, token):
    """Show the Google Analytics token or not"""
    return ShowGoogleAnalyticsJS()


register.tag(googleanalyticsjs)


class ShowGoogleAnalytics404JS(template.Node):
    """Show the Google Analytics"""

    def render(self, context):
        """Render the Google Analytics token or not"""
        code = getattr(settings, "GOOGLE_ANALYTICS_CODE", False)

        try:
            site = context.get("site").domain
        except AttributeError:
            site = "Unknown"

        if not code:
            return "<!-- Google Universal Analytics not included because you haven't set the settings.GOOGLE_ANALYTICS_CODE variable! -->"

        if "user" in context and context["user"] and context["user"].is_staff:
            return "<!-- Google Universal Analytics not included because you are a staff user! -->"

        if settings.DEBUG:
            return "<!-- Google Universal Analytics not included because you are in Debug mode! -->"

        return (
            """
            <script>
              (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
              (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
              m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
              })(window,document,'script','//www.google-analytics.com/analytics.js','ga');

              ga('create', '"""
            + code
            + """', '"""
            + site
            + """', { cookieDomain: '"""
            + site
            + """' });
              ga('send', 'event', '404', 'Visit', "'" + document.location.pathname + "'" );
            </script>"""
        )


def googleanalytics404js(parser, token):
    """Show the Google Analytics token for a 404"""
    return ShowGoogleAnalytics404JS()


register.tag(googleanalytics404js)
