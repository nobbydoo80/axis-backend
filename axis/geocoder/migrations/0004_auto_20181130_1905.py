# Generated by Django 1.11.16 on 2018-11-30 19:05

import axis.core.fields
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("geocoder", "0003_auto_20181008_1816"),
    ]

    operations = [
        migrations.AlterField(
            model_name="geocoderesponse",
            name="place",
            field=axis.core.fields.AxisJSONField(blank=True, default=dict),
        ),
    ]
