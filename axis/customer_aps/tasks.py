"""tasks.py: Django customer_aps"""


import csv
import datetime
import os
import tempfile
import time

from celery import shared_task
from celery.utils.log import get_task_logger
from django.contrib.auth import get_user_model
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.core.files import File
from django.db import IntegrityError
from django.db.models import Q
from infrastructure.utils import elapsed_time
from localflavor.us.us_states import STATES_NORMALIZED

from axis.customer_aps.exports.home_data_custom import APSHomeDataCustomExport
from axis.customer_aps.messages import ApsHomeUtilityCustomExportCompletedMessage
from axis.customer_aps.utils import geolocate_apshome
from axis.filehandling.log_storage import LogStorage
from axis.filehandling.models import AsynchronousProcessedDocument
from axis.filehandling.models import ResultObjectLog
from axis.filehandling.utils import CSVParser, get_physical_file
from axis.home.models import Home
from .forms import APSHomeStringForm
from .models import APSHome

__author__ = "Steven Klass"
__date__ = "6/11/12 7:07 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

logger = get_task_logger(__name__)
User = get_user_model()

METERSET_UNIQUE_HEADER_COLUMN = "Premise ID"
METERSET_DIALECT = csv.excel
METERSET_DATE_FORMAT = "%m/%d/%Y"
METERSET_FIELD_MAP = [
    ("premise_id", "Premise ID"),
    ("raw_street_line_1", "Premise Address"),
    ("raw_city", "Premise City"),
    ("raw_state", "Premise State"),
    ("raw_zip", "Premise Zip"),
    ("raw_lot_number", "LOT"),
]

METERSET_FIELD_CLEAN_MAP = [("raw_state", lambda x: STATES_NORMALIZED[x.lower()])]

METERSET_ADDRESS_LINE = "{raw_lot_number} {raw_street_line_1} " "{raw_city}, {raw_state} {raw_zip}"

DESIRED_COLUMNS = [
    "builder_org",
    "subdivision",
    "lot_number",
    "street_line1",
    "city",
    "zipcode",
    "certificate_date",
    "floorplan",
    "county",
]

COLUMN_MAP = {
    "builder": "builder_org",
    "community": "community",
    "lot": "lot_number",
    "subdivision": "subdivision",
    "address": "street_line1",
    "city": "city",
    "zipcode": "zipcode",
    "zip": "zipcode",
    "energystarcertification": "certificate_date",
    "hers score": "hers_index",
    "hersscore": "hers_index",
    "floorplan": "floorplan",
    "plan": "floorplan",
    "county": "county",
}


@shared_task(time_limit=60 * 60 * 6)
def process_metersets_task(company_id, user_id, result_object_id, **kwargs):
    start_time = time.time()
    from axis.filehandling.models import AsynchronousProcessedDocument

    log = kwargs["log"] = kwargs.get("log", logger)

    result_object = AsynchronousProcessedDocument.objects.get(id=result_object_id)
    result_log = ResultObjectLog(result_object_id=result_object.id)

    if None in [company_id, user_id, result_object_id]:
        lerrors = "Missing items {0}".format(", ".join([company_id, user_id, result_object_id]))
        result_log.update(errors=lerrors, raise_errors=True)
        return

    user = User.objects.get(id=user_id)
    company = result_object.company
    document = result_object.document

    try:
        filename, notes = get_physical_file(document.name)
        result_log.update(result_list=notes, raise_errors=True)
    except AttributeError:
        filename, notes = document, ["Using document string {0}".format(document)]
        result_log.update(warnings=notes, raise_errors=True)

    msg = "{user} submitted {document} for processing with task {task} [{task_id}]"
    log.info(
        msg.format(
            user=user,
            document=filename,
            task=result_object.task_name,
            task_id=result_object.task_id,
        )
    )
    #
    # -- Here is where the real work begins --
    #

    log.info(
        "Starting on {document} for {company}".format(
            document=result_object.filename(), company=company
        )
    )

    try:
        csv = CSVParser(
            filename=filename,
            uniq_header_column=METERSET_UNIQUE_HEADER_COLUMN,
            dialect=METERSET_DIALECT,
        )
        csv.get_columns()
        start_row = csv.row
    except TypeError as _err:
        err = "This does not appear to be a CSV document - %r" % _err
        result_log.update(errors=err, raise_errors=True)
        return
    except (IndexError, ValueError) as err:
        if isinstance(err.args[0], list):
            for error in err.args[0]:
                result_log.update(errors=error, raise_errors=True)
        else:
            result_log.update(errors=err, raise_errors=True)
        return
    except StopIteration:
        err = 'Unable to find header row in CSV File. Looking for "{}" Column'.format(
            METERSET_UNIQUE_HEADER_COLUMN
        )
        result_log.update(errors=err, raise_errors=True)
        return

    results = csv.get_results_dictionary_list(start_row=start_row)

    if not len(results):
        lerrors = "This appears to be a valid document without any data.  Is it all on one line?"
        result_log.update(errors=lerrors, raise_errors=True)

    final_results = []
    for item in results:
        if len(item.keys()) <= 1:
            continue

        # Aps provides files with export data at the beginning and end.
        # If we encounter a line with no meterset date, we can assume we've reached the end of data
        # and have gone back to export details.
        if not item["Initial Meter Set Date"]:
            continue

        stat = "{}/{}".format(results.index(item) + 1, len(results))
        result_log.update(latest="{} Validating Meterset".format(stat))
        try:
            ms_date = datetime.datetime.strptime(
                item["Initial Meter Set Date"], METERSET_DATE_FORMAT
            )
        except:
            err = "Unable to get a Meter Set Date expecting {} - got {}".format(
                METERSET_DATE_FORMAT, item["Initial Meter Set Date"]
            )
            result_log.update(errors=err, line_no=item["row_number"])
            continue

        if kwargs.get("suffix") in ["TRL", "GLN"]:
            kwargs["suffix"] = kwargs["suffix"][0:2]

        data = {"meterset_date": ms_date}
        for key, mapping in METERSET_FIELD_MAP:
            data[key] = item[mapping]

        for key, cleaner in METERSET_FIELD_CLEAN_MAP:
            data[key] = cleaner(data[key])

        try:
            geolocation_matches = geolocate_apshome(**data)
        except IntegrityError:
            msg = "Integrity Error geolocate_apshome with kwargs {}".format(data)
            log.error(msg, exc_info=1, extra={"user": user})
            geolocation_matches = []

        if len(geolocation_matches) == 1:
            match = geolocation_matches[0]
            geocoded_data = match.get_normalized_fields()
            values = [
                "street_line1",
                "street_line2",
                "state",
                "zipcode",
                "confirmed_address",
                "latitude",
                "longitude",
            ]
            data.update({k: geocoded_data.get(k, None) for k in values})
            data["geocode_response"] = match.id
            data["city"] = geocoded_data.get("city").id if geocoded_data.get("city") else None
            data["county"] = geocoded_data.get("county").id if geocoded_data.get("county") else None
            data["metro"] = geocoded_data.get("metro").id if geocoded_data.get("metro") else None
            data["climate_zone"] = (
                geocoded_data.get("climate_zone").id if geocoded_data.get("climate_zone") else None
            )
        else:
            addr = METERSET_ADDRESS_LINE.format(**data)
            data.update(geolocate_apshome(return_lookup=True, **data))
            city = data.get("city")
            if city:
                data["city"] = city.id
                data["county"] = city.county.id if city.county else None
                data["metro"] = city.county.metro.id if city.county and city.county.metro else None
                data["climate_zone"] = (
                    city.county.climate_zone.id
                    if city.county and city.county.climate_zone
                    else None
                )
            data["confirmed_address"] = False
            log.warning(
                "%s - Address provided was not confirmed - %s", "process_metersets_task", addr
            )

        try:
            instance = APSHome.objects.get(premise_id=item[dict(METERSET_FIELD_MAP)["premise_id"]])
        except ObjectDoesNotExist:
            instance = None

        form = APSHomeStringForm(data=data, instance=instance)

        if not form.is_valid():
            for key, issues in form.errors.items():
                for issue in issues:
                    result_log.update(
                        errors="Key: {} - {}".format(key, issue), line_no=item["row_number"]
                    )
            continue

        form.cleaned_data["row_number"] = item["row_number"]
        final_results.append(form.cleaned_data)
    if len(result_log.get_errors()):
        result_log.update(raise_errors=True)
        return

    result_log.update(latest="Stage two validation complete")

    created, matched, confirmed, updated = 0, 0, 0, 0
    for item in final_results:
        stat = "{}/{}".format(final_results.index(item) + 1, len(final_results))
        result_log.update(latest="{} Processing Meterset".format(stat))

        premise_id = item.pop("premise_id")
        row_number = item.pop("row_number")
        defaults = item.pop("defaults", dict())
        for k, v in defaults.items():
            item[k] = v

        # log.warning(item)
        need_save = False
        aps_home, create = APSHome.objects.get_or_create(premise_id=premise_id, defaults=item)

        try:
            _haps_home = APSHome.objects.get(id=aps_home.id).history.most_recent()
            if user and _haps_home.history_user is None:
                _haps_home.history_user = user
                _haps_home.save()
        except AttributeError:
            pass

        if create:
            created += 1
        else:
            if aps_home.home:
                item["home"] = aps_home.home
            for key, value in item.items():
                if key.startswith("_"):
                    continue
                try:
                    if getattr(aps_home, key) != item[key]:
                        log.debug("Updating %s: %s", key, value)
                        need_save = True
                        setattr(aps_home, key, value)
                except AttributeError:
                    pass
            if need_save:
                aps_home.save()

                try:
                    _haps_home = APSHome.objects.get(id=aps_home.id).history.most_recent()
                    if user and _haps_home.history_user is None:
                        _haps_home.history_user = user
                        _haps_home.save()
                except AttributeError:
                    pass

                updated += 1

        if not aps_home.confirmed_address:
            geolocate_apshome(object=aps_home, **item)
            try:
                _haps_home = APSHome.objects.get(id=aps_home.id).history.most_recent()
                if user and _haps_home.history_user is None:
                    _haps_home.history_user = user
                    _haps_home.save()
            except AttributeError:
                pass

        if aps_home.confirmed_address:
            confirmed += 1

        result_log.update(latest="{} Processing Part 1 of Meterset".format(stat))
        try:
            url = '<a href="{}">{}</a>'.format(aps_home.get_absolute_url(), aps_home)
        except:
            url = aps_home
        ctype = "Created" if create else "Used existing"
        ctype = ctype if not need_save else "Updated existing"
        msg = "{} APS Meterset {} with a{} address".format(
            ctype,
            url,
            " confirmed" if aps_home.confirmed_address else "n unconfirmed",
        )

        if aps_home.confirmed_address and not aps_home.home:
            try:
                if aps_home.street_line2 in ["", None]:
                    home = Home.objects.get(
                        Q(street_line2__isnull=True) | Q(street_line2=""),
                        apshome__isnull=True,
                        street_line1=aps_home.street_line1,
                        city=aps_home.city,
                        state=aps_home.state,
                        zipcode=aps_home.zipcode,
                    )
                else:
                    home = Home.objects.get(
                        apshome__isnull=True,
                        street_line2=aps_home.street_line2,
                        street_line1=aps_home.street_line1,
                        city=aps_home.city,
                        state=aps_home.state,
                        zipcode=aps_home.zipcode,
                    )
                aps_home.home = home
                aps_home.save()
                matched += 1

                try:
                    _haps_home = APSHome.objects.get(id=aps_home.id).history.most_recent()
                    if user and _haps_home.history_user is None:
                        _haps_home.history_user = user
                        _haps_home.save()
                except AttributeError:
                    pass
            except (MultipleObjectsReturned, ObjectDoesNotExist):
                pass

        result_log.update(latest="{} Processing Part 2 of Meterset".format(stat))
        if aps_home.home:
            try:
                hurl = '<a href="{}">{}</a>'.format(aps_home.home.get_absolute_url(), aps_home.home)
            except ImportError:
                hurl = aps_home.home
            msg += " which matches to {}".format(hurl)

        log.info("%s Processing part 3", stat)
        result_log.update(info=msg, line_no=row_number)

    if document.name not in filename:
        try:
            os.remove(filename)
        except WindowsError:
            log.error("Windows Error unable to remove %r", filename)
            pass

    pct = float(confirmed) / float(len(final_results)) if len(final_results) else 0
    messages = [
        "Created {}/{} homes".format(created, len(final_results)),
        "Updated {}/{} homes".format(updated, len(final_results)),
        "Matched {}/{} homes to Axis Homes".format(matched, len(final_results)),
        "Geocode {}/{} ({:.2%}) homes".format(confirmed, len(final_results), pct),
    ]

    result_log.update(info=messages)

    #
    # -- End of real work --
    #

    msg = "Completed processing {document} for {company} in {elapsed}"
    log.info(
        msg.format(
            document=result_object.filename(),
            company=company,
            elapsed=elapsed_time(time.time() - start_time).long_fmt,
        )
    )
    return msg.format(
        document=result_object.filename(),
        company=company,
        elapsed=elapsed_time(time.time() - start_time).long_fmt,
    )


@shared_task(time_limit=60 * 60 * 2)
def update_metersets_task():
    """
    Crontab to update daily the unmatched metersets
    """

    start_time = time.time()
    from axis.incentive_payment.models import IncentivePaymentStatus
    from axis.home.models import Home
    from axis.customer_aps.utils import APSAutoMatcher

    _ipp = IncentivePaymentStatus.objects.filter(
        home_status__home__apshome__isnull=True, home_status__eep_program__owner__slug="aps"
    )
    home_ids = _ipp.exclude(state="complete").values_list("home_status__home_id", flat=True)
    homes = Home.objects.filter(id__in=home_ids)
    matches = []

    for home in homes:
        exclude_ids = [x[1].id for x in matches]
        auto = APSAutoMatcher(axis_home=home, show_detail=False)
        try:
            match = auto.automatch(exclude_ids=exclude_ids)
            if not match:
                continue
            matches.append((home, auto.aps_home, auto.match_reason, auto.issues))
            auto.update()
            auto.align()
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            pass

    msg = "Completed %(task)s in %(elapsed_time)s"
    logger.info(
        msg,
        {
            "task": "update_metersets_task",
            "elapsed_time": elapsed_time(time.time() - start_time).long_fmt,
        },
    )


@shared_task(time_limit=60 * 60 * 2, bind=True)
def export_custom_aps_home_data(self, result_object_id, **kwargs):
    """Generated custom APS data in XLS format"""

    self.update_state(state="STARTED")
    app_log = LogStorage(model_id=result_object_id)

    async_processed_document = AsynchronousProcessedDocument.objects.get(id=result_object_id)

    async_processed_document.task_id = self.request.id
    async_processed_document.task_name = self.name
    async_processed_document.save()

    user_id = kwargs.get("user_id", None)
    user = User.objects.get(id=user_id) if user_id else None

    msg = "{user} requested home data export task {task} [{task_id}]"
    app_log.info(
        msg.format(
            user=user,
            task=async_processed_document.task_name,
            task_id=async_processed_document.task_id,
        )
    )

    prefix = "APS-Custom-Export_"
    export = APSHomeDataCustomExport(log=app_log, **kwargs)
    new_filename = tempfile.NamedTemporaryFile(delete=True, suffix=".xlsx", prefix=prefix)
    export.write(output=new_filename)

    app_log.info("New file saved %s", os.path.basename(new_filename.name))

    async_processed_document.document = File(new_filename, name=os.path.basename(new_filename.name))
    async_processed_document.save()

    self.update_state(state="SUCCESS")
    app_log.update_model(throttle_seconds=None)

    # Send alert/email to user when task completes.
    ApsHomeUtilityCustomExportCompletedMessage(
        url=async_processed_document.get_absolute_url()
    ).send(user=user)
