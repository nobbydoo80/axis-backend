# Generated by Django 3.1.6 on 2021-04-06 14:32

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("customer_hirl", "0140_merge_20210401_1516"),
    ]

    operations = [
        migrations.AddField(
            model_name="hirlproject",
            name="jamis_milestoned",
            field=models.BooleanField(
                default=False,
                help_text="Populating automatically from Billing Rule file that generated by JAMIS service",
            ),
        ),
        migrations.AddField(
            model_name="historicalhirlproject",
            name="jamis_milestoned",
            field=models.BooleanField(
                default=False,
                help_text="Populating automatically from Billing Rule file that generated by JAMIS service",
            ),
        ),
    ]