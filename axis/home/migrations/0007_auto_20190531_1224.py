# Generated by Django 1.11.17 on 2019-05-31 12:24

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0006_validationdata"),
    ]

    operations = [
        migrations.AlterField(
            model_name="eepprogramhomestatus",
            name="created_date",
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name="eepprogramhomestatus",
            name="modified_date",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name="historicaleepprogramhomestatus",
            name="created_date",
            field=models.DateTimeField(blank=True, editable=False),
        ),
        migrations.AlterField(
            model_name="historicaleepprogramhomestatus",
            name="modified_date",
            field=models.DateTimeField(blank=True, editable=False),
        ),
        migrations.AlterField(
            model_name="historicalhome",
            name="created_date",
            field=models.DateTimeField(blank=True, editable=False),
        ),
        migrations.AlterField(
            model_name="historicalhome",
            name="modified_date",
            field=models.DateTimeField(blank=True, editable=False),
        ),
        migrations.AlterField(
            model_name="home",
            name="created_date",
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name="home",
            name="modified_date",
            field=models.DateTimeField(auto_now=True),
        ),
    ]
