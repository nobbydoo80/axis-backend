"""views.py: Django search"""


import logging

from django.core.exceptions import FieldError
from django.contrib.auth.mixins import LoginRequiredMixin

from appsearch.views import BaseSearchView
from appsearch.utils import Searcher

__author__ = "Autumn Valenta"
__date__ = "2012/10/12 3:22:30 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class RelationshipSearcher(Searcher):
    """Filters all searches by the ``relationship`` ties."""

    def build_queryset(self, model, query, queryset=None):
        """
        Changes the default queryset to the one returned by ``filter_by_user()``, a common method
        on the managers of relationship-enabled model classes.  The current state of the
        relationship app is that the querysets returned by the ``RelationshipManager`` don't support
        the methods on the manager itself, making chain-filtering after the automatic queryset
        construction not possible.  Instead, the pre-filtered queryset is slipped in as the base
        for the ``query`` to be applied.

        """
        try:
            queryset = model.objects.filter_by_user(self.request.user, show_attached=False)
        except (FieldError, TypeError):
            try:
                queryset = model.objects.filter_by_user(self.request.user)
            except (TypeError, ValueError):
                queryset = model.objects

        return super(RelationshipSearcher, self).build_queryset(model, query, queryset=queryset)


class SearchView(LoginRequiredMixin, BaseSearchView):
    """Configures our search view with a custom ``Searcher`` instance and template."""

    searcher_class = RelationshipSearcher
    template_name = "search/search.html"
