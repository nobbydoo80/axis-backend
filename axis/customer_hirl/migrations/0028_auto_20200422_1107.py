# Generated by Django 1.11.26 on 2020-04-22 11:07

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("customer_hirl", "0027_auto_20200420_1848"),
    ]

    operations = [
        migrations.AddField(
            model_name="historicalverifieragreement",
            name="company_with_multiple_verifiers",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="verifieragreement",
            name="company_with_multiple_verifiers",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="verifieragreement",
            name="provided_services",
            field=models.ManyToManyField(blank=True, to="customer_hirl.ProvidedService"),
        ),
    ]