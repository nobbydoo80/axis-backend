__author__ = "Autumn Valenta"
__date__ = "7/20/15 1:57 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]

from django.core.paginator import Paginator, InvalidPage
from rest_framework.pagination import PageNumberPagination


class AxisPageNumberPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 1000

    def paginate_queryset(self, queryset, request, view=None):
        """
        Customize original pagination class and ignore invalid page error
        """
        page_size = self.get_page_size(request)
        if not page_size:
            return None

        paginator = self.django_paginator_class(queryset, page_size)
        page_number = self.get_page_number(request, paginator)

        try:
            self.page = paginator.page(page_number)
        except InvalidPage:
            self.page = paginator.page(1)

        if paginator.num_pages > 1 and self.template is not None:
            # The browsable API should display pagination controls.
            self.display_page_controls = True

        self.request = request
        return list(self.page)

    def get_next_link(self):
        link = super(AxisPageNumberPagination, self).get_next_link()
        if link:
            link = link.replace("http://", "https://")
        return link

    def get_previous_link(self):
        link = super(AxisPageNumberPagination, self).get_previous_link()
        if link:
            link = link.replace("http://", "https://")
        return link


class NoCountPaginator(Paginator):
    """
    Using to speed up Admin pages with a lot of objects and do not count total pages
    """

    @property
    def count(self):
        return 999999999
