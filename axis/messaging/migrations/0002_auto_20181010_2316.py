# Generated by Django 1.11.16 on 2018-10-10 23:16

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("messaging", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="historicaldigestpreference",
            name="history_change_reason",
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="historicalmessagingpreference",
            name="history_change_reason",
            field=models.CharField(max_length=100, null=True),
        ),
    ]
