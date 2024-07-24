# Generated by Django 1.11.26 on 2020-05-15 11:08

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("customer_hirl", "0046_auto_20200515_1102"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="historicalverifieragreement",
            name="insurance_expiration_date",
        ),
        migrations.RemoveField(
            model_name="historicalverifieragreement",
            name="insurance_policy_number",
        ),
        migrations.RemoveField(
            model_name="historicalverifieragreement",
            name="insurance_start_date",
        ),
        migrations.RemoveField(
            model_name="verifieragreement",
            name="insurance_expiration_date",
        ),
        migrations.RemoveField(
            model_name="verifieragreement",
            name="insurance_policy_number",
        ),
        migrations.RemoveField(
            model_name="verifieragreement",
            name="insurance_start_date",
        ),
        migrations.AddField(
            model_name="coidocument",
            name="expiration_date",
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name="coidocument",
            name="policy_number",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name="coidocument",
            name="start_date",
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name="historicalcoidocument",
            name="expiration_date",
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name="historicalcoidocument",
            name="policy_number",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name="historicalcoidocument",
            name="start_date",
            field=models.DateField(null=True),
        ),
    ]
