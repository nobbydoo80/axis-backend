# Generated by Django 1.11.17 on 2019-05-21 23:11

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("customer_hirl", "0003_builderagreement_historicalbuilderagreement"),
    ]

    operations = [
        migrations.AlterField(
            model_name="builderagreement",
            name="agreement_expiration_date",
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name="builderagreement",
            name="agreement_start_date",
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name="builderagreement",
            name="insurance_expiration_date",
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name="builderagreement",
            name="insurance_start_date",
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name="historicalbuilderagreement",
            name="agreement_expiration_date",
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name="historicalbuilderagreement",
            name="agreement_start_date",
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name="historicalbuilderagreement",
            name="insurance_expiration_date",
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name="historicalbuilderagreement",
            name="insurance_start_date",
            field=models.DateField(null=True),
        ),
    ]