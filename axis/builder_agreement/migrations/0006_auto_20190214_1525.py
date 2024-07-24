# Generated by Django 1.11.17 on 2019-02-14 15:25

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("builder_agreement", "0005_auto_20181010_2316"),
    ]

    operations = [
        migrations.AlterField(
            model_name="builderagreement",
            name="start_date",
            field=models.DateField(
                blank=True,
                help_text="The start date that this agreement begins.  Incentive Payments will be checked against this.",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="builderagreement",
            name="total_lots",
            field=models.IntegerField(
                blank=True, help_text="Total number of lots this agreement covers", null=True
            ),
        ),
        migrations.AlterField(
            model_name="historicalbuilderagreement",
            name="start_date",
            field=models.DateField(
                blank=True,
                help_text="The start date that this agreement begins.  Incentive Payments will be checked against this.",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="historicalbuilderagreement",
            name="total_lots",
            field=models.IntegerField(
                blank=True, help_text="Total number of lots this agreement covers", null=True
            ),
        ),
    ]