# Generated by Django 1.11.17 on 2019-06-07 15:59

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("customer_hirl", "0012_auto_20190607_1501"),
    ]

    operations = [
        migrations.RenameField(
            model_name="builderagreement",
            old_name="executed_agreement",
            new_name="signed_agreement",
        ),
        migrations.RenameField(
            model_name="historicalbuilderagreement",
            old_name="executed_agreement",
            new_name="signed_agreement",
        ),
    ]
