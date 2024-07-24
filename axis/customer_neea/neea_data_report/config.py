"""App configs."""


from csv import DictReader
import io
import logging

from django.conf import settings

from axis.core import customers

__author__ = "Autumn Valenta"
__date__ = "10/10/2018 5:00 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]

log = logging.getLogger(__name__)

settings = getattr(settings, "NEEA_DATA_REPORT", {})


# pylint: disable=invalid-name
class NEEADataReportConfig(customers.ExtensionConfig):
    """NEEA Data Report import config."""

    def import_certifications(self, filename):
        from axis.home.disambiguation.utils import import_certification
        from .models import NEEACertification
        from .forms import CertificationForm

        log.info("Reading %r...", filename)

        # IMPORTANT: We received a file with BOM encoding. We can remove the
        # special encoding as things settle.
        with io.open(filename, "r", encoding="utf-8-sig") as f:
            for i, record in enumerate(DictReader(f)):
                log.info("Importing record %d: %s", i + 1, record["StreetAddress"])

                form = CertificationForm(data=record)
                if form.is_valid():
                    # Get fully modded data from save() before continuing.
                    # We should switch to a serializer and remove candidate creation from save().
                    form.save(commit=False)

                    obj, _ = NEEACertification.objects.update_or_create(
                        registry_id=form.cleaned_data["registry_id"], defaults=form.cleaned_data
                    )
                    import_certification(obj)
                else:
                    log.error("Form not valid: %r", form.errors)


config = NEEADataReportConfig
