# Generated by Django 1.11.16 on 2018-10-10 23:16

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("scheduling", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="historicalconstructionstatus",
            name="history_change_reason",
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="historicaltask",
            name="history_change_reason",
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="historicaltasktype",
            name="history_change_reason",
            field=models.CharField(max_length=100, null=True),
        ),
    ]