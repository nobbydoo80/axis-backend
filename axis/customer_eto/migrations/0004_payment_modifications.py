# Generated by Django 1.11.17 on 2019-05-30 22:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("customer_eto", "0003_auto_20181010_2316"),
    ]

    operations = [
        migrations.AddField(
            model_name="fasttracksubmission",
            name="original_builder_electric_incentive",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True),
        ),
        migrations.AddField(
            model_name="fasttracksubmission",
            name="original_builder_gas_incentive",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True),
        ),
        migrations.AddField(
            model_name="fasttracksubmission",
            name="original_builder_incentive",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True),
        ),
        migrations.AddField(
            model_name="fasttracksubmission",
            name="original_rater_electric_incentive",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True),
        ),
        migrations.AddField(
            model_name="fasttracksubmission",
            name="original_rater_gas_incentive",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True),
        ),
        migrations.AddField(
            model_name="fasttracksubmission",
            name="original_rater_incentive",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True),
        ),
        migrations.AddField(
            model_name="fasttracksubmission",
            name="payment_change_datetime",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="fasttracksubmission",
            name="payment_change_user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="fasttracksubmission",
            name="payment_revision_comment",
            field=models.TextField(blank=True, null=True, verbose_name="Payment change comment"),
        ),
        migrations.AddField(
            model_name="historicalfasttracksubmission",
            name="original_builder_electric_incentive",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True),
        ),
        migrations.AddField(
            model_name="historicalfasttracksubmission",
            name="original_builder_gas_incentive",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True),
        ),
        migrations.AddField(
            model_name="historicalfasttracksubmission",
            name="original_builder_incentive",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True),
        ),
        migrations.AddField(
            model_name="historicalfasttracksubmission",
            name="original_rater_electric_incentive",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True),
        ),
        migrations.AddField(
            model_name="historicalfasttracksubmission",
            name="original_rater_gas_incentive",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True),
        ),
        migrations.AddField(
            model_name="historicalfasttracksubmission",
            name="original_rater_incentive",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True),
        ),
        migrations.AddField(
            model_name="historicalfasttracksubmission",
            name="payment_change_datetime",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="historicalfasttracksubmission",
            name="payment_change_user",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="historicalfasttracksubmission",
            name="payment_revision_comment",
            field=models.TextField(blank=True, null=True, verbose_name="Payment change comment"),
        ),
    ]
