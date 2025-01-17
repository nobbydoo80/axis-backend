# Generated by Django 3.1.3 on 2020-12-30 12:18

import axis.core.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("certification", "0013_merge_20201204_1437"),
    ]

    operations = [
        migrations.AlterField(
            model_name="certifiableobject",
            name="settings",
            field=axis.core.fields.AxisJSONField(),
        ),
        migrations.AlterField(
            model_name="historicalcertifiableobject",
            name="settings",
            field=axis.core.fields.AxisJSONField(),
        ),
        migrations.AlterField(
            model_name="historicalworkflowstatus",
            name="data",
            field=axis.core.fields.AxisJSONField(),
        ),
        migrations.AlterField(
            model_name="historicalworkflowstatusstatelog",
            name="from_state",
            field=models.CharField(choices=[], max_length=100),
        ),
        migrations.AlterField(
            model_name="historicalworkflowstatusstatelog",
            name="to_state",
            field=models.CharField(choices=[], max_length=100),
        ),
        migrations.AlterField(
            model_name="workflowstatus",
            name="data",
            field=axis.core.fields.AxisJSONField(),
        ),
        migrations.AlterField(
            model_name="workflowstatusstatelog",
            name="from_state",
            field=models.CharField(choices=[], max_length=100),
        ),
        migrations.AlterField(
            model_name="workflowstatusstatelog",
            name="to_state",
            field=models.CharField(choices=[], max_length=100),
        ),
    ]
