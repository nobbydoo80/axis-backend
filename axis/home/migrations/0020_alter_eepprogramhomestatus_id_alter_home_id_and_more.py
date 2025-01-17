# Generated by Django 4.0.7 on 2022-09-14 19:58

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("subdivision", "0009_alter_historicalsubdivision_builder_org_and_more"),
        ("company", "0030_alter_company_city_alter_company_group_and_more"),
        ("home", "0019_alter_eepprogramhomestatus_options_and_more"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="standarddisclosuresettings",
            unique_together={("owner", "company", "subdivision", "home_status")},
        ),
    ]
