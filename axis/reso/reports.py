"""reports.py: Django reso"""


import codecs
import logging
import re
from collections import OrderedDict


__author__ = "Steven Klass"
__date__ = "9/26/17 12:39"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)

if __name__ == "__main__":
    from django.apps import apps as django_app

    if not django_app.apps_ready:
        import django

        django.setup()

    # user = get_user_model().objects.get(username="rjohnson")
    # from axis.reso.tasks import assign_data_to_reso_models
    # assign_data_to_reso_models(38242)

    from axis.reso.models import ResoHome, ResoGreenVerification

    label_names = OrderedDict(
        [
            (f.name, "ListingKeyNumeric__{}".format(f.name))
            for f in ResoHome._meta.fields
            if f.name.lower() != f.name
        ]
    )
    label_names["City"] = "ListingKeyNumeric__City__name"
    label_names["CountyOrParish"] = "ListingKeyNumeric__CountyOrParish__name"
    label_names.update(
        OrderedDict(
            [
                (f.name, "{}".format(f.name))
                for f in ResoGreenVerification._meta.fields
                if f.name != "id"
            ]
        )
    )

    output = []
    output.append("\t".join(label_names.keys()))
    for reso_item in ResoGreenVerification.objects.all().values_list(*label_names.values()):
        output.append(
            "\t".join(["%s".encode("utf8") % (f if f is not None else "") for f in reso_item])
        )

    with codecs.open("output_reso.csv", "w", "utf-8") as f:
        for line in output:
            f.write("{}\n".format(line))

    output = []
    output.append("\t".join(["Field", "Type", "Max Length", "Allow Null", "choices"]))
    for field in ResoHome._meta.fields + ResoGreenVerification._meta.fields:
        if field.name.lower() == field.name:
            continue
        data = [
            field.name,
            re.sub(r"Field", "", field.__class__.__name__).upper(),
            field.max_length,
            field.null,
        ]
        choices = (
            [
                ("{}".format(x[0]).encode("utf8"), "{}".format(x[1]).encode("utf8"))
                for x in field.choices
            ]
            if len(field.choices)
            else None
        )
        data.append(choices)
        output.append("\t".join(["%s".encode("utf8") % (f if f is not None else "") for f in data]))

    with codecs.open("output_reso_metadata.csv", "w", "utf-8") as f:
        for line in output:
            f.write("{}\n".format(line))
