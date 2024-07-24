# Generated by Django 1.11.16 on 2018-10-08 18:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("geographic", "0001_initial"),
        ("geocoder", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="geocode",
            name="raw_city",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="geographic.City",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="geocode",
            unique_together=set([("raw_address", "entity_type")]),
        ),
    ]
