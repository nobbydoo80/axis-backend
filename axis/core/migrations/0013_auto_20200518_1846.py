# Generated by Django 1.11.26 on 2020-05-18 18:46

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0012_auto_20200422_1918"),
    ]

    operations = [
        migrations.AddField(
            model_name="historicaluser",
            name="ngbs_verifier_id",
            field=models.CharField(blank=True, max_length=64, verbose_name="NGBS Verifier ID"),
        ),
        migrations.AddField(
            model_name="user",
            name="ngbs_verifier_id",
            field=models.CharField(blank=True, max_length=64, verbose_name="NGBS Verifier ID"),
        ),
    ]
