"""managers.py: Django geocoder"""
import logging
import re
import string
from difflib import SequenceMatcher

from django.apps import apps
from django.conf import settings
from django.db import models
from django.db.models import When, Case
from django.db.models.query import QuerySet

from axis.geographic.utils.legacy import format_geographic_input

__author__ = "Steven Klass"
__date__ = "2/20/14 4:18 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)

app = apps.get_app_config("geocoder")


class GeocodeReponseMixin(object):
    def confirmed(self):
        initial_count = "Unk"
        if log.isEnabledFor(settings.DEBUG):
            initial_count = self.filter().count()
        confirmed_ids = []
        for response in self.filter():
            if response.broker.place.is_confirmed:
                confirmed_ids.append(response.id)
        if log.isEnabledFor(settings.DEBUG) or True:
            log.debug(
                "Filtered from %s down to %s confirmed addresses.",
                initial_count,
                len(confirmed_ids),
            )
        return self.filter(id__in=confirmed_ids).distinct()

    def statistically_likely(self, close_probability_ratio=None, return_higest=False):
        """This does some basic analysis to compare what was entered vs what was returned to
        find the most likely matches."""

        regex = re.compile(r"[%s]" % re.escape("""!"#$%&'()*,./:;<=>?@[]^_`{|}~"""))

        likely_ids = {}

        first_pass = True
        raw = []

        for response in self.filter():
            if response.broker.place.country not in app.SUPPORTED_COUNTRIES:
                continue

            # Dynamically build this up so we use what we have.
            result = []

            if response.geocode.entity_type == "city":
                result.append(response.broker.place.city)
                if first_pass:
                    raw.append(response.geocode.raw_address.split(",")[0])
                # We really need to have a county for US based stuff.
                if response.broker.place.country == "US" and not response.broker.place.county:
                    log.info(f"Missing county for {response.pk} moving on.")
                    raw = raw if not first_pass else []
                    continue

            if response.geocode.entity_type == "intersection" and response.geocode.raw_cross_roads:
                result.append(response.broker.place.intersection)
                if first_pass:
                    raw.append(response.geocode.raw_address.split(",")[0])

            if response.geocode.entity_type == "street_address":
                if response.geocode.raw_street_line1:
                    result.append(response.broker.place.street_line1)
                    if first_pass:
                        raw.append(response.geocode.raw_street_line1)

                if response.geocode.raw_street_line2:
                    if response.broker.place.street_line2:
                        result.append(response.broker.place.street_line2)
                    if first_pass:
                        raw.append(response.geocode.raw_street_line2)

                if response.geocode.raw_city:
                    result.append(response.broker.place.city)
                    if first_pass:
                        raw.append(response.geocode.raw_city.name)

            if response.geocode.raw_county:
                _county = str(response.broker.place.county)
                match = re.search(
                    r"(.*)(County|Parish|City|Borough|Municipality|Municipio|Census Area)",
                    _county,
                    flags=re.I,
                )
                if match:
                    _county = match.group(1).strip()
                result.append(_county)
                if first_pass:
                    raw.append(response.geocode.raw_county.name)

            if response.geocode.raw_state:
                result.append(response.broker.place.state)
                if first_pass:
                    raw.append(response.geocode.raw_state.abbr)

            if response.geocode.entity_type == "street_address":
                if response.geocode.raw_zipcode:
                    result.append(response.broker.place.zipcode)
                    if first_pass:
                        raw.append(response.geocode.raw_zipcode)

            if response.geocode.raw_country:
                result.append(response.broker.place.country)
                if first_pass:
                    raw.append(response.geocode.raw_country.abbr)

            if first_pass:
                raw = regex.sub("", " ".join([x.lower() for x in raw if x]))
                raw = re.sub(r" {2,}", " ", raw)
                first_pass = False

            result = regex.sub("", " ".join([x.lower() for x in result if x]))
            result = re.sub(r" {2,}", " ", result)

            if close_probability_ratio is None:
                close_probability_ratio = app.CLOSE_PROXIMITY_RATIO_LOOKUP[
                    response.geocode.entity_type
                ]

            likely = SequenceMatcher(lambda x: x == " ", raw, result).ratio()
            log.info(
                f"{response.geocode.entity_type.capitalize()} {response.engine} probability of "
                f"{likely:.1%} (Target: {close_probability_ratio:.1%}) between "
                f"{raw!r} and {result!r}."
            )
            if likely > close_probability_ratio:
                likely_ids[response.id] = likely

        case_statement = Case(*[When(pk=k, then=v) for k, v in likely_ids.items()], default=0.0)
        values = (
            self.filter(pk__in=likely_ids.keys())
            .annotate(match_probability=case_statement)
            .order_by("-match_probability")
        )

        if return_higest and likely_ids:
            return values.filter(id=values.first().pk)
        return values

    def logically_reduce(self):
        """Return the top choice for each engine"""

        # Prioritize Google first (-engine)
        values = self.filter().order_by("-match_probability", "-engine")
        # We only want one per engine in the top (total_engines slots)
        total_engines = 2
        data = values.values_list("pk", "engine", "match_probability")[:total_engines]
        pks, engines, probabilities = [], [], []
        for pk, engine, probability in data:
            if engine in engines:
                continue

            if not len(probabilities):
                probabilities.append(probability)
                pks.append(pk)
                continue

            # If the last probability equals the current probability continue on.
            last_probability = probabilities[:][-1]
            if last_probability == probability:
                continue

            # If the delta between the last > 5% stop
            delta = (last_probability - probability) / last_probability
            if delta > 0.04:
                break
            probabilities.append(probability)
            pks.append(pk)

        return self.filter(id__in=pks).order_by("-match_probability")


class GeocodeReponseQuerySet(QuerySet, GeocodeReponseMixin):
    pass


class GeocodeReponseManager(models.Manager, GeocodeReponseMixin):
    def get_queryset(self):
        return GeocodeReponseQuerySet(self.model, using=self._db)


class GeocodeManager(models.Manager):
    def get_matches(self, raw_address=None, only_confirmed=True, **kwargs):
        if not raw_address:
            raw_address, raw_parts, entity_type = format_geographic_input(**kwargs)
        else:
            entity_type = kwargs.pop("entity_type")
            raw_parts = {}

        if not raw_address or (not entity_type and kwargs.values()):
            log.error("No entity type %s  found for kwargs: %s", entity_type, kwargs)
            return self.model.objects.none()

        # Make sure None items are made blank for db
        raw_parts = {k: (v or "") for k, v in raw_parts.items()}
        if raw_parts["raw_county"] == "":
            raw_parts["raw_county"] = None
        if raw_parts["raw_state"] == "":
            raw_parts["raw_state"] = None

        geocode, created = self.get_or_create(
            raw_address=raw_address,
            entity_type=entity_type,
            defaults=dict(immediate=kwargs.get("immediate", True), **raw_parts),
        )

        log.info(
            f"{'Create' if created else 'Using'} {entity_type} Geocode [{geocode.id}] {raw_address}"
        )

        if not created and geocode.can_be_geocoded:
            log.debug("Not created and triggering a geocode")
            geocode.save()

        geocode.refresh_from_db()

        return geocode.get_valid_responses(only_confirmed=only_confirmed)
