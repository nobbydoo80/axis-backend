# Generated by Django 1.11.26 on 2020-07-02 16:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("customer_hirl", "0057_auto_20200630_1724"),
    ]

    operations = [
        migrations.AlterField(
            model_name="builderagreement",
            name="shipping_geocode",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="geocoder.Geocode",
            ),
        ),
        migrations.AlterField(
            model_name="verifieragreement",
            name="shipping_geocode",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="geocoder.Geocode",
            ),
        ),
    ]
