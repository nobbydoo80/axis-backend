# Generated by Django 2.2 on 2020-08-11 08:39

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("customer_eto", "0010_auto_20200515_1921"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="fasttracksubmission",
            options={"ordering": ("id",), "verbose_name": "ProjectTracking Submission"},
        ),
    ]
