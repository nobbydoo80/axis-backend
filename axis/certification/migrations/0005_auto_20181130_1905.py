# Generated by Django 1.11.16 on 2018-11-30 19:05

import axis.core.fields
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("certification", "0004_auto_20181010_2316"),
    ]

    operations = [
        migrations.AlterField(
            model_name="certifiableobject",
            name="settings",
            field=axis.core.fields.AxisJSONField(default=dict),
        ),
        migrations.AlterField(
            model_name="historicalcertifiableobject",
            name="settings",
            field=axis.core.fields.AxisJSONField(default=dict),
        ),
        migrations.AlterField(
            model_name="historicalworkflowstatus",
            name="data",
            field=axis.core.fields.AxisJSONField(default=dict),
        ),
        migrations.AlterField(
            model_name="workflowstatus",
            name="data",
            field=axis.core.fields.AxisJSONField(default=dict),
        ),
    ]
