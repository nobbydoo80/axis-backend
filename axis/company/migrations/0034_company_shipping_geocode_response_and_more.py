# Generated by Django 4.1.7 on 2023-03-29 11:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("geocoder", "0014_geocode_raw_country"),
        ("company", "0033_auto_20230224_1051"),
    ]

    operations = [
        migrations.AddField(
            model_name="company",
            name="shipping_geocode_response",
            field=models.ForeignKey(
                blank=True,
                help_text="Selected by user in case of multiple valid results, automatically when we have one result and empty when geocode do not have valid results",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="geocoder.geocoderesponse",
            ),
        ),
        migrations.AddField(
            model_name="historicalarchitectorganization",
            name="shipping_geocode_response",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                help_text="Selected by user in case of multiple valid results, automatically when we have one result and empty when geocode do not have valid results",
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="geocoder.geocoderesponse",
            ),
        ),
        migrations.AddField(
            model_name="historicalbuilderorganization",
            name="shipping_geocode_response",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                help_text="Selected by user in case of multiple valid results, automatically when we have one result and empty when geocode do not have valid results",
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="geocoder.geocoderesponse",
            ),
        ),
        migrations.AddField(
            model_name="historicalcommunityownerorganization",
            name="shipping_geocode_response",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                help_text="Selected by user in case of multiple valid results, automatically when we have one result and empty when geocode do not have valid results",
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="geocoder.geocoderesponse",
            ),
        ),
        migrations.AddField(
            model_name="historicalcompany",
            name="shipping_geocode_response",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                help_text="Selected by user in case of multiple valid results, automatically when we have one result and empty when geocode do not have valid results",
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="geocoder.geocoderesponse",
            ),
        ),
        migrations.AddField(
            model_name="historicaldeveloperorganization",
            name="shipping_geocode_response",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                help_text="Selected by user in case of multiple valid results, automatically when we have one result and empty when geocode do not have valid results",
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="geocoder.geocoderesponse",
            ),
        ),
        migrations.AddField(
            model_name="historicaleeporganization",
            name="shipping_geocode_response",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                help_text="Selected by user in case of multiple valid results, automatically when we have one result and empty when geocode do not have valid results",
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="geocoder.geocoderesponse",
            ),
        ),
        migrations.AddField(
            model_name="historicalgeneralorganization",
            name="shipping_geocode_response",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                help_text="Selected by user in case of multiple valid results, automatically when we have one result and empty when geocode do not have valid results",
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="geocoder.geocoderesponse",
            ),
        ),
        migrations.AddField(
            model_name="historicalhvacorganization",
            name="shipping_geocode_response",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                help_text="Selected by user in case of multiple valid results, automatically when we have one result and empty when geocode do not have valid results",
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="geocoder.geocoderesponse",
            ),
        ),
        migrations.AddField(
            model_name="historicalproviderorganization",
            name="shipping_geocode_response",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                help_text="Selected by user in case of multiple valid results, automatically when we have one result and empty when geocode do not have valid results",
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="geocoder.geocoderesponse",
            ),
        ),
        migrations.AddField(
            model_name="historicalqaorganization",
            name="shipping_geocode_response",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                help_text="Selected by user in case of multiple valid results, automatically when we have one result and empty when geocode do not have valid results",
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="geocoder.geocoderesponse",
            ),
        ),
        migrations.AddField(
            model_name="historicalraterorganization",
            name="shipping_geocode_response",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                help_text="Selected by user in case of multiple valid results, automatically when we have one result and empty when geocode do not have valid results",
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="geocoder.geocoderesponse",
            ),
        ),
        migrations.AddField(
            model_name="historicalutilityorganization",
            name="shipping_geocode_response",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                help_text="Selected by user in case of multiple valid results, automatically when we have one result and empty when geocode do not have valid results",
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="geocoder.geocoderesponse",
            ),
        ),
    ]
