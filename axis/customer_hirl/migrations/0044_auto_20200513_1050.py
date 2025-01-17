# Generated by Django 1.11.26 on 2020-05-13 10:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("geocoder", "0008_merge_20200427_1427"),
        ("customer_hirl", "0043_auto_20200513_0909"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="builderagreement",
            name="mailing_address_city",
        ),
        migrations.RemoveField(
            model_name="builderagreement",
            name="mailing_address_state",
        ),
        migrations.RemoveField(
            model_name="builderagreement",
            name="mailing_address_street_line1",
        ),
        migrations.RemoveField(
            model_name="builderagreement",
            name="mailing_address_street_line2",
        ),
        migrations.RemoveField(
            model_name="builderagreement",
            name="mailing_address_zipcode",
        ),
        migrations.RemoveField(
            model_name="builderagreement",
            name="shipping_address_city",
        ),
        migrations.RemoveField(
            model_name="builderagreement",
            name="shipping_address_state",
        ),
        migrations.RemoveField(
            model_name="builderagreement",
            name="shipping_address_street_line1",
        ),
        migrations.RemoveField(
            model_name="builderagreement",
            name="shipping_address_street_line2",
        ),
        migrations.RemoveField(
            model_name="builderagreement",
            name="shipping_address_zipcode",
        ),
        migrations.RemoveField(
            model_name="historicalbuilderagreement",
            name="mailing_address_city",
        ),
        migrations.RemoveField(
            model_name="historicalbuilderagreement",
            name="mailing_address_state",
        ),
        migrations.RemoveField(
            model_name="historicalbuilderagreement",
            name="mailing_address_street_line1",
        ),
        migrations.RemoveField(
            model_name="historicalbuilderagreement",
            name="mailing_address_street_line2",
        ),
        migrations.RemoveField(
            model_name="historicalbuilderagreement",
            name="mailing_address_zipcode",
        ),
        migrations.RemoveField(
            model_name="historicalbuilderagreement",
            name="shipping_address_city",
        ),
        migrations.RemoveField(
            model_name="historicalbuilderagreement",
            name="shipping_address_state",
        ),
        migrations.RemoveField(
            model_name="historicalbuilderagreement",
            name="shipping_address_street_line1",
        ),
        migrations.RemoveField(
            model_name="historicalbuilderagreement",
            name="shipping_address_street_line2",
        ),
        migrations.RemoveField(
            model_name="historicalbuilderagreement",
            name="shipping_address_zipcode",
        ),
        migrations.AddField(
            model_name="builderagreement",
            name="mailing_geocode",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="+",
                to="geocoder.Geocode",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="builderagreement",
            name="shipping_geocode",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="+",
                to="geocoder.Geocode",
            ),
        ),
        migrations.AddField(
            model_name="historicalbuilderagreement",
            name="mailing_geocode",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="geocoder.Geocode",
            ),
        ),
        migrations.AddField(
            model_name="historicalbuilderagreement",
            name="shipping_geocode",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="geocoder.Geocode",
            ),
        ),
    ]
