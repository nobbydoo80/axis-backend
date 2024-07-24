"""certification.py - Axis"""

__author__ = "Steven K"
__date__ = "12/12/21 13:32"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import datetime
import logging
from typing import Optional

from django.apps import apps
from django.db import models
from django.db.models import Q, QuerySet

log = logging.getLogger(__name__)
app = apps.get_app_config("customer_hirl")


class HIRLLegacyCertificationQuerySet(models.QuerySet):
    def _filter_field_date(
        self,
        queryset: models.QuerySet["HIRLLegacyCertification"],
        field: str = "data__CertificateSentDate",
        start_datetime: Optional[datetime.datetime] = None,
        end_datetime: Optional[datetime.datetime] = None,
    ):
        if start_datetime is None:
            start_datetime = datetime.datetime(1990, 1, 1).replace(tzinfo=datetime.timezone.utc)
        if end_datetime is None:
            _now = datetime.datetime.now(datetime.timezone.utc)
            _end_date = _now + datetime.timedelta(hours=24 - _now.hour)
            end_datetime = datetime.datetime(
                _end_date.year, _end_date.month, _end_date.day
            ).replace(tzinfo=datetime.timezone.utc)

        def fix_datetime(value: str) -> datetime.datetime:
            return datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S").replace(
                tzinfo=datetime.timezone.utc
            )

        keep = []

        for pk, _datestr in queryset.values_list("pk", field):
            try:
                _date = fix_datetime(_datestr)
            except TypeError:
                raise TypeError(f"Unable to convert {_datestr} for {pk}")
            if start_datetime <= _date < end_datetime:
                keep.append(pk)
        return self.filter(pk__in=keep)

    def base_certified(
        self,
        start_datetime: Optional[datetime.datetime] = None,
        end_datetime: Optional[datetime.datetime] = None,
        eep_program: Optional["EEPProgram"] = None,
        us_state: Optional[str] = None,
    ):
        """This was based on a file named Desktop Browser Certification Activity Report Layout.cs"""
        from axis.customer_hirl.sync.us_states import HIRL_INTERNAL_US_STATES

        secondary_filter = {"data__fkCertificationStatus": 7}
        if eep_program:
            reverse_legacy_map = {v: k for k, v in app.NGBS_PROGRAM_NAMES.items()}
            if isinstance(eep_program, QuerySet):
                secondary_filter["scoring_path_name__in"] = [
                    reverse_legacy_map.get(e.slug) for e in eep_program
                ]
            else:
                secondary_filter["scoring_path_name"] = reverse_legacy_map.get(eep_program.slug)
        if us_state:
            state_id = next(
                (x["ID"] for x in HIRL_INTERNAL_US_STATES if x["StateAbbr"] == us_state)
            )
            secondary_filter["data__State"] = state_id

        queryset = self.exclude(
            Q(data__CertificateNumber="") | Q(data__CertificateNumber=None),
            data__CertificateSentDate__isnull=False,
        ).filter(**secondary_filter)

        if start_datetime or end_datetime:
            return self._filter_field_date(
                queryset, "data__CertificateSentDate", start_datetime, end_datetime
            )
        return queryset

    def legacy_certified(
        self,
        start_datetime: Optional[datetime.datetime] = None,
        end_datetime: Optional[datetime.datetime] = None,
        eep_program: Optional["EEPProgram"] = None,
        us_state: Optional[str] = None,
    ):
        """These are only legacy certified not captured in a new project"""
        return self.base_certified(start_datetime, end_datetime, eep_program, us_state).filter(
            project__isnull=True
        )
