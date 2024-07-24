# Generated by Django 1.11.17 on 2019-04-10 18:54

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("analytics", "0001_initial"),
        ("eep_program", "0011_shallow_migrate_to_cr2"),
    ]

    operations = [
        migrations.AddField(
            model_name="eepprogram",
            name="metrics",
            field=models.ManyToManyField(related_name="programs", to="analytics.Metric"),
        ),
    ]
