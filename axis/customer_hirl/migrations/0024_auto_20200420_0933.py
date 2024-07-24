# Generated by Django 1.11.26 on 2020-04-20 09:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("geographic", "0002_auto_20190531_1224"),
        ("customer_hirl", "0023_auto_20200417_0834"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="historicalverifieragreement",
            name="mailing_address_city",
        ),
        migrations.RemoveField(
            model_name="historicalverifieragreement",
            name="mailing_address_state",
        ),
        migrations.RemoveField(
            model_name="historicalverifieragreement",
            name="mailing_address_street_line1",
        ),
        migrations.RemoveField(
            model_name="historicalverifieragreement",
            name="mailing_address_street_line2",
        ),
        migrations.RemoveField(
            model_name="historicalverifieragreement",
            name="mailing_address_zipcode",
        ),
        migrations.RemoveField(
            model_name="historicalverifieragreement",
            name="shipping_address_city",
        ),
        migrations.RemoveField(
            model_name="historicalverifieragreement",
            name="shipping_address_state",
        ),
        migrations.RemoveField(
            model_name="historicalverifieragreement",
            name="shipping_address_street_line1",
        ),
        migrations.RemoveField(
            model_name="historicalverifieragreement",
            name="shipping_address_street_line2",
        ),
        migrations.RemoveField(
            model_name="historicalverifieragreement",
            name="shipping_address_zipcode",
        ),
        migrations.RemoveField(
            model_name="verifieragreement",
            name="mailing_address_city",
        ),
        migrations.RemoveField(
            model_name="verifieragreement",
            name="mailing_address_state",
        ),
        migrations.RemoveField(
            model_name="verifieragreement",
            name="mailing_address_street_line1",
        ),
        migrations.RemoveField(
            model_name="verifieragreement",
            name="mailing_address_street_line2",
        ),
        migrations.RemoveField(
            model_name="verifieragreement",
            name="mailing_address_zipcode",
        ),
        migrations.RemoveField(
            model_name="verifieragreement",
            name="shipping_address_city",
        ),
        migrations.RemoveField(
            model_name="verifieragreement",
            name="shipping_address_state",
        ),
        migrations.RemoveField(
            model_name="verifieragreement",
            name="shipping_address_street_line1",
        ),
        migrations.RemoveField(
            model_name="verifieragreement",
            name="shipping_address_street_line2",
        ),
        migrations.RemoveField(
            model_name="verifieragreement",
            name="shipping_address_zipcode",
        ),
        migrations.AddField(
            model_name="historicalverifieragreement",
            name="administrative_contact_email",
            field=models.EmailField(default="axis@example.com", max_length=30),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="historicalverifieragreement",
            name="administrative_contact_first_name",
            field=models.CharField(default="", max_length=30),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="historicalverifieragreement",
            name="administrative_contact_last_name",
            field=models.CharField(default="", max_length=30),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="historicalverifieragreement",
            name="administrative_contact_phone_number",
            field=models.CharField(default="", max_length=30),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="historicalverifieragreement",
            name="applicant_cell_number",
            field=models.CharField(default="", max_length=30),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="historicalverifieragreement",
            name="applicant_email",
            field=models.EmailField(default="axis@example.com", max_length=30),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="historicalverifieragreement",
            name="applicant_first_name",
            field=models.CharField(default="", max_length=30),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="historicalverifieragreement",
            name="applicant_last_name",
            field=models.CharField(default="", max_length=30),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="historicalverifieragreement",
            name="applicant_phone_number",
            field=models.CharField(default="", max_length=30),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="historicalverifieragreement",
            name="applicant_place",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="geographic.Place",
            ),
        ),
        migrations.AddField(
            model_name="historicalverifieragreement",
            name="applicant_title",
            field=models.CharField(default="", max_length=30),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="historicalverifieragreement",
            name="mailing_place",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="geographic.Place",
            ),
        ),
        migrations.AddField(
            model_name="historicalverifieragreement",
            name="shipping_place",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="geographic.Place",
            ),
        ),
        migrations.AddField(
            model_name="verifieragreement",
            name="administrative_contact_email",
            field=models.EmailField(default="axis@example.com", max_length=30),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="verifieragreement",
            name="administrative_contact_first_name",
            field=models.CharField(default="", max_length=30),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="verifieragreement",
            name="administrative_contact_last_name",
            field=models.CharField(default="", max_length=30),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="verifieragreement",
            name="administrative_contact_phone_number",
            field=models.CharField(default="", max_length=30),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="verifieragreement",
            name="applicant_cell_number",
            field=models.CharField(default="", max_length=30),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="verifieragreement",
            name="applicant_email",
            field=models.EmailField(default="", max_length=30),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="verifieragreement",
            name="applicant_first_name",
            field=models.CharField(default="", max_length=30),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="verifieragreement",
            name="applicant_last_name",
            field=models.CharField(default="", max_length=30),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="verifieragreement",
            name="applicant_phone_number",
            field=models.CharField(default="", max_length=30),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="verifieragreement",
            name="applicant_place",
            field=models.ForeignKey(
                default="",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="customer_hirl_verifier_agreement_applicant_place",
                to="geographic.Place",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="verifieragreement",
            name="applicant_title",
            field=models.CharField(default="", max_length=30),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="verifieragreement",
            name="mailing_place",
            field=models.ForeignKey(
                default="",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="customer_hirl_verifier_agreement_mailing_place",
                to="geographic.Place",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="verifieragreement",
            name="shipping_place",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="customer_hirl_verifier_agreement_shipping_place",
                to="geographic.Place",
            ),
        ),
    ]