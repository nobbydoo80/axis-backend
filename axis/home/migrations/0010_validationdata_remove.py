# Generated by Django 1.11.17 on 2019-04-19 18:55

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0009_auto_20190826_2024"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="historicalvalidationdata",
            name="history_user",
        ),
        migrations.RemoveField(
            model_name="historicalvalidationdata",
            name="home_status",
        ),
        migrations.RemoveField(
            model_name="validationdata",
            name="home_status",
        ),
        migrations.DeleteModel(
            name="HistoricalValidationData",
        ),
        migrations.DeleteModel(
            name="ValidationData",
        ),
    ]