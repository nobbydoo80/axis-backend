# Generated by Django 4.0.7 on 2022-10-19 19:44

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("customer_hirl", "0215_remove_hirlproject_is_require_full_certification_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="hirlprojectregistration",
            name="are_all_homes_in_ld_seeking_certification",
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="historicalhirlprojectregistration",
            name="are_all_homes_in_ld_seeking_certification",
            field=models.BooleanField(blank=True, null=True),
        ),
    ]
