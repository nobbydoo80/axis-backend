# Generated by Django 1.11.26 on 2020-04-29 12:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("filehandling", "0007_auto_20200415_1542"),
        ("customer_hirl", "0033_auto_20200427_1525"),
    ]

    operations = [
        migrations.AddField(
            model_name="historicalverifieragreement",
            name="company_officer_title",
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name="historicalverifieragreement",
            name="signed_agreement",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="filehandling.CustomerDocument",
            ),
        ),
        migrations.AddField(
            model_name="verifieragreement",
            name="company_officer_title",
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name="verifieragreement",
            name="signed_agreement",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="filehandling.CustomerDocument",
            ),
        ),
        migrations.AlterField(
            model_name="historicalverifieragreement",
            name="administrative_contact_email",
            field=models.EmailField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="historicalverifieragreement",
            name="administrative_contact_first_name",
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AlterField(
            model_name="historicalverifieragreement",
            name="administrative_contact_last_name",
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AlterField(
            model_name="historicalverifieragreement",
            name="administrative_contact_phone_number",
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AlterField(
            model_name="historicalverifieragreement",
            name="company_officer_email",
            field=models.EmailField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="historicalverifieragreement",
            name="company_officer_first_name",
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AlterField(
            model_name="historicalverifieragreement",
            name="company_officer_last_name",
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AlterField(
            model_name="historicalverifieragreement",
            name="company_officer_phone_number",
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AlterField(
            model_name="verifieragreement",
            name="administrative_contact_email",
            field=models.EmailField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="verifieragreement",
            name="administrative_contact_first_name",
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AlterField(
            model_name="verifieragreement",
            name="administrative_contact_last_name",
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AlterField(
            model_name="verifieragreement",
            name="administrative_contact_phone_number",
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AlterField(
            model_name="verifieragreement",
            name="company_officer_email",
            field=models.EmailField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="verifieragreement",
            name="company_officer_first_name",
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AlterField(
            model_name="verifieragreement",
            name="company_officer_last_name",
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AlterField(
            model_name="verifieragreement",
            name="company_officer_phone_number",
            field=models.CharField(blank=True, max_length=30),
        ),
    ]
