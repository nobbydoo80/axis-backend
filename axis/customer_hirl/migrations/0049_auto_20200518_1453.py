# Generated by Django 1.11.26 on 2020-05-18 14:53

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("customer_hirl", "0048_auto_20200518_0924"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="builderagreement",
            name="marketing_contact_fax_number",
        ),
        migrations.RemoveField(
            model_name="builderagreement",
            name="payment_contact_fax_number",
        ),
        migrations.RemoveField(
            model_name="builderagreement",
            name="primary_contact_fax_number",
        ),
        migrations.RemoveField(
            model_name="builderagreement",
            name="secondary_contact_fax_number",
        ),
        migrations.RemoveField(
            model_name="builderagreement",
            name="website_contact_fax_number",
        ),
        migrations.RemoveField(
            model_name="historicalbuilderagreement",
            name="marketing_contact_fax_number",
        ),
        migrations.RemoveField(
            model_name="historicalbuilderagreement",
            name="payment_contact_fax_number",
        ),
        migrations.RemoveField(
            model_name="historicalbuilderagreement",
            name="primary_contact_fax_number",
        ),
        migrations.RemoveField(
            model_name="historicalbuilderagreement",
            name="secondary_contact_fax_number",
        ),
        migrations.RemoveField(
            model_name="historicalbuilderagreement",
            name="website_contact_fax_number",
        ),
    ]
