# Generated by Django 3.2.7 on 2021-09-21 17:36

import axis.core.fields
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("customer_hirl", "0183_auto_20210913_2120"),
    ]

    operations = [
        migrations.AddField(
            model_name="hirlproject",
            name="system_notes",
            field=axis.core.fields.AxisJSONField(
                blank=True,
                encoder=axis.core.fields.AxisJSONEncoder,
                help_text="Helps to identify legacy NGBS projects from different sources. This field can be used to store any information during import",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="historicalhirlproject",
            name="system_notes",
            field=axis.core.fields.AxisJSONField(
                blank=True,
                encoder=axis.core.fields.AxisJSONEncoder,
                help_text="Helps to identify legacy NGBS projects from different sources. This field can be used to store any information during import",
                null=True,
            ),
        ),
    ]
