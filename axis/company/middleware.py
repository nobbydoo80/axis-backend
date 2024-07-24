"""middleware.py: Django company"""


import hashlib
import logging

from django.conf import settings
from django.core.cache import cache
from django.urls import reverse

from .models import Company

__author__ = "Steven Klass"
__date__ = "12/1/14 8:39 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


def assign_cached_attributes(company, force=False):
    """A cached version of a company given a company_id"""

    # Copy value of ``Org.is_sample_eligible`` to the local object
    # NOTE: This is something I don't think we're using and might need to be removed.
    # See the models.py comments left in 2016 concerning removing the field altogether.
    is_sample_eligible = False
    if company.company_type in ("rater", "provider"):
        is_sample_eligible = (
            Company.objects.filter(id=company.id)
            .values_list("is_sample_eligible", flat=True)
            .first()
        )
    company.is_sample_eligible = is_sample_eligible

    # Read/commit simplified sponsor_info in cache
    # Assign result to company for easy access in core.context_processors.menu_data() and
    # site template "base-footer.html"
    cache_key = hashlib.sha1(
        "company__{company_id}__sponsor_info".format(company_id=company.id).encode("utf-8")
    ).hexdigest()
    sponsor_info = None if force else cache.get(cache_key)

    # Verify company.pk is available to avoid querying for NonCompany instances
    # The virtualized company.sponsor_info attribute has already defaulted to []
    if sponsor_info is None:
        try:
            sponsor_info = list(company.sponsors.distinct().values("name", "slug", "home_page"))
        except AttributeError:
            sponsor_info = []
        for item in sponsor_info:
            item["url"] = item["home_page"]
            if not item["url"]:
                _kw = {"type": company.company_type, "pk": company.id}
                item["url"] = reverse("company:view", kwargs=_kw)
        msg = "Setting sponsor info for %(company)s (%(company_id)s) to %(sponsor_count)s sponsors"
        msg_kw = {"company": company, "company_id": company.id, "sponsor_count": len(sponsor_info)}
        # log.info(msg, msg_kw)
        cache.set(cache_key, sponsor_info, settings.COMPANY_SPONSOR_INFO_CACHE_DURATION)
        company.sponsor_info = sponsor_info

    return company


class CompanyMiddleware:
    class NonCompany(object):
        """Dummy company that holds blank local attribute values."""

        def __init__(self):
            self.sponsor_info = []
            self.sponsor_list = []
            company_fields = tuple(
                f.name for f in Company._meta.get_fields() if f.get_internal_type() != "ForeignKey"
            )
            for k in company_fields + ("pk", "is_sample_eligible"):
                setattr(self, k, None)

    non_company = NonCompany()

    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        assert hasattr(request, "user"), (
            "The company middleware requires auth middleware to be "
            "installed. Edit your MIDDLEWARE setting to insert "
            "'django.contrib.auth.middleware.AuthenticationMiddleware'."
        )

        valid = request.user.is_authenticated and request.user.company_id and request.user.company

        if not valid:
            company = self.non_company
        else:
            company = request.user.company
        company = assign_cached_attributes(company)
        request.company = company

        return self.get_response(request)
