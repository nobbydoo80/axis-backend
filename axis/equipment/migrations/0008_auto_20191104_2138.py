# Generated by Django 1.11.17 on 2019-11-04 21:38

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("company", "0004_auto_20190826_2024"),
        ("equipment", "0007_auto_20191104_1715"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="equipmentsponsorstatus",
            unique_together=set([("equipment", "company")]),
        ),
    ]
