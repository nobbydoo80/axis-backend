# Generated by Django 1.11.26 on 2020-04-22 12:15

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("customer_hirl", "0029_verifieragreement_counties"),
    ]

    operations = [
        migrations.AlterField(
            model_name="historicalverifieragreement",
            name="applicant_cell_number",
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AlterField(
            model_name="verifieragreement",
            name="applicant_cell_number",
            field=models.CharField(blank=True, max_length=30),
        ),
    ]
