# Generated by Django 2.2 on 2020-07-28 12:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("qa", "0008_auto_20200713_2005"),
    ]

    operations = [
        migrations.AlterField(
            model_name="observationtype",
            name="company",
            field=models.ForeignKey(
                limit_choices_to={"company_type": "qa"},
                on_delete=django.db.models.deletion.CASCADE,
                to="company.Company",
            ),
        ),
    ]
