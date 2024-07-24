# Generated by Django 3.2.9 on 2021-11-10 14:06

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("user_management", "0037_auto_20210920_1253"),
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
                    ("master-verifier", "Master Verifier"),
                ],
                max_length=45,
            ),
        ),
    ]
