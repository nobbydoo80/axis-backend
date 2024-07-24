"""admin.py: checklist"""


from django.contrib import admin
from django_input_collection.models import get_input_model

__author__ = "Steven Klass"
__date__ = "5/27/13 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

CollectedInput = get_input_model()

# unregister CollectedInput admin class from django_input_collection to override it
admin.site.unregister(CollectedInput)


@admin.register(CollectedInput)
class CollectedInputAdmin(admin.ModelAdmin):
    list_display = ["id", "instrument_measure", "data", "home", "program"]
    list_filter = ["date_created", "date_modified"]
    search_fields = ["data", "instrument__measure__id", "home__street_line1"]
    date_hierarchy = "date_created"
    raw_id_fields = ("home", "home_status", "instrument", "user", "collection_request")

    def instrument_measure(self, obj):
        return obj.instrument.measure

    def program(self, obj):
        return obj.home_status.eep_program
