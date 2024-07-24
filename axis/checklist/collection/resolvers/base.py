"""Base resolvers"""


from django_input_collection.collection import Resolver


__author__ = "Autumn Valenta"
__date__ = "2012-10-08 1:48:00 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions.Consulting. All rights reserved."
__credits__ = [
    "Steven Klass",
]
__license__ = "See the file LICENSE.txt for licensing information."


class CollectorMethodResolver(Resolver):
    name = "collector"
    pattern = r"(?P<dotted_path>\d+)"

    def resolve(self, instrument, dotted_path, **context):
        collection_request = instrument.collection_request
        home_status = collection_request.getattr("eepprogramhomestatus", None)

        if home_status is None:  # CollectionRequest is not on a homestatus
            return False

        return {}

        # inputs = instrument.collectedinput_set.filter_for_context(**context)
        # values = list(inputs.values_list('data', flat=True))
        #
        # # Avoid list coercion at this step so that match types not requiring this query won't end
        # # up hitting the database.
        # suggested_values = instrument.suggested_responses.values_list('data', flat=True)
        #
        # return {
        #     'data': values,
        #     'suggested_values': suggested_values,
        # }
