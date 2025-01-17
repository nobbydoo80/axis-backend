# Generated by Django 3.2.14 on 2022-07-19 15:20

from django.db import migrations, models
import django.db.models.deletion


def update_countries(apps, schema_editor):
    from axis.geographic.utils.country import resolve_country

    usa = resolve_country("US")
    pr = resolve_country("PR")
    vi = resolve_country("VI")

    ModelObj = apps.get_model("geocoder", "Geocode")
    ModelObj.objects.exclude(raw_county__state__in=["PR", "VI"]).update(raw_country=usa)
    ModelObj.objects.exclude(raw_city__county__state__in=["PR", "VI"]).update(raw_country=usa)
    ModelObj.objects.filter(raw_county__state__in=["PR"]).update(raw_country=pr, raw_county=None)
    ModelObj.objects.exclude(raw_city__county__state__in=["PR"]).update(
        raw_country=pr, raw_county=None
    )
    ModelObj.objects.filter(raw_county__state__in=["VI"]).update(raw_country=vi, raw_county=None)
    ModelObj.objects.exclude(raw_city__county__state__in=["PR"]).update(
        raw_country=vi, raw_county=None
    )


class Migration(migrations.Migration):
    dependencies = [
        ("geographic", "0006_auto_20220719_1459"),
        ("geocoder", "0013_auto_20211021_1933"),
    ]

    operations = [
        migrations.AddField(
            model_name="geocode",
            name="raw_country",
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.CASCADE, to="geographic.country"
            ),
        ),
        migrations.RunPython(update_countries),
    ]
