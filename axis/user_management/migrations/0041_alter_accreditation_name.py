# Generated by Django 3.2.9 on 2021-11-17 09:04

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("user_management", "0040_auto_20211111_1812"),
    ]

    operations = [
        migrations.AlterField(
            model_name="accreditation",
            name="name",
            field=models.CharField(
                choices=[
                    ("ngbs-2020", "NGBS 2020"),
                    ("ngbs-2015", "NGBS 2015"),
                    ("ngbs-2012", "NGBS 2012"),
                    ("master-verifier", "NGBS Master Verifier"),
                    ("ngbs-wri-verifier", "NGBS WRI Verifier"),
                    ("ngbs-green-field-rep", "NGBS Green Field Rep"),
                ],
                max_length=45,
            ),
        ),
    ]
