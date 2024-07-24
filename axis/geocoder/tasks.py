"""tasks.py: Django geocoder"""
from urllib import error

from celery import shared_task
from celery.exceptions import Retry
from celery.utils.log import get_task_logger
from geopy.exc import GeocoderQueryError

__author__ = "Peter Landry"
__date__ = "12/4/13 5:47 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Peter Landry",
]

logger = get_task_logger(__name__)


@shared_task(queue="priority", default_retry_delay=30, max_retries=5)
def get_responses(geocode_id, engine_name, **kwargs):
    """Gets the geocode responses"""
    from .models import GeocodeResponse, Geocode

    log = kwargs.get("log", logger)

    raw_address = kwargs.get("raw_address")
    entity_type = kwargs.get("entity_type")
    timeout = kwargs.get("timeout")

    try:
        geocode = Geocode.objects.get(id=geocode_id)
        raw_address = geocode.raw_address
        entity_type = geocode.entity_type
        engine = geocode.get_engine_instance(engine_name)
    except Geocode.DoesNotExist:
        from .engines import GEOCODER_ENGINES

        engine = GEOCODER_ENGINES[engine_name]({"timeout": timeout})

    try:
        response = engine.geocode(raw_address)
    except Exception as exc:
        try:
            get_responses.retry(exc=exc)
            return
        except GeocoderQueryError:
            msg = "Unable to lookup up %s - %s from %s [%s] GQueryError"
            log.warning(msg, entity_type, raw_address, engine_name, geocode_id)
            response = []
        except (error.HTTPError, Retry):
            raise
        except Exception as err:
            msg = "Unable to lookup up %s - %s from %s [%s] %s"
            log.error(msg, entity_type, raw_address, engine_name, geocode_id, err, exc_info=True)
            response = []

    # response should be a list of json "places", see .engines.[geocoder].parse_result
    for place in response:
        try:
            GeocodeResponse.objects.update_or_create(
                geocode_id=geocode_id, engine=engine_name, place=place
            )
        except GeocodeResponse.MultipleObjectsReturned:
            # previous code could create multiple GeocodeResponses for one engine
            # after replace code to update_or_create we need to catch MultipleObjectsReturned
            # and delete duplicates
            responses_to_delete = GeocodeResponse.objects.filter(
                geocode_id=geocode_id, engine=engine_name, place=place
            ).values_list("id", flat=True)[1:]
            GeocodeResponse.objects.filter(id__in=list(responses_to_delete)).delete()

    log.debug("%s received %s geocode for %r", engine_name.capitalize(), entity_type, raw_address)
