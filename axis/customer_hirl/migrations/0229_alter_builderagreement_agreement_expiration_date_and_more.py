# Generated by Django 4.1.7 on 2023-04-07 08:21

import axis.core.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("company", "0030_alter_company_city_alter_company_group_and_more"),
        ("geocoder", "0014_geocode_raw_country"),
        ("filehandling", "0013_customerdocument_login_required_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("customer_hirl", "0228_alter_hirlprojectregistration_options_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="builderagreement",
            name="agreement_expiration_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="builderagreement",
            name="agreement_start_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="builderagreement",
            name="certifying_document",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="filehandling.customerdocument",
            ),
        ),
        migrations.AlterField(
            model_name="builderagreement",
            name="data",
            field=axis.core.fields.AxisJSONField(
                blank=True, default=dict, encoder=axis.core.fields.AxisJSONEncoder
            ),
        ),
        migrations.AlterField(
            model_name="builderagreement",
            name="mailing_geocode",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="geocoder.geocode",
            ),
        ),
        migrations.AlterField(
            model_name="builderagreement",
            name="marketing_contact_cell_number",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="builderagreement",
            name="marketing_contact_email_address",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="builderagreement",
            name="marketing_contact_first_name",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="builderagreement",
            name="marketing_contact_last_name",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="builderagreement",
            name="marketing_contact_phone_number",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="builderagreement",
            name="marketing_contact_title",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="builderagreement",
            name="payment_contact_cell_number",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="builderagreement",
            name="payment_contact_email_address",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="builderagreement",
            name="payment_contact_first_name",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="builderagreement",
            name="payment_contact_last_name",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="builderagreement",
            name="payment_contact_phone_number",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="builderagreement",
            name="payment_contact_title",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="builderagreement",
            name="primary_contact_cell_number",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="builderagreement",
            name="primary_contact_email_address",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="builderagreement",
            name="primary_contact_first_name",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="builderagreement",
            name="primary_contact_last_name",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="builderagreement",
            name="primary_contact_phone_number",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="builderagreement",
            name="primary_contact_title",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="builderagreement",
            name="secondary_contact_cell_number",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="builderagreement",
            name="secondary_contact_email_address",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="builderagreement",
            name="secondary_contact_first_name",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="builderagreement",
            name="secondary_contact_last_name",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="builderagreement",
            name="secondary_contact_phone_number",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="builderagreement",
            name="secondary_contact_title",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="builderagreement",
            name="shipping_geocode",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="geocoder.geocode",
            ),
        ),
        migrations.AlterField(
            model_name="builderagreement",
            name="signed_agreement",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="filehandling.customerdocument",
            ),
        ),
        migrations.AlterField(
            model_name="builderagreement",
            name="signer_email",
            field=models.EmailField(
                blank=True,
                help_text="Using for direct DocuSign workflow without AXIS User",
                max_length=254,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="builderagreement",
            name="signer_name",
            field=models.CharField(
                blank=True,
                help_text="Using for direct DocuSign workflow without AXIS User",
                max_length=100,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="builderagreement",
            name="website",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="builderagreement",
            name="website_contact_cell_number",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="builderagreement",
            name="website_contact_email_address",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="builderagreement",
            name="website_contact_first_name",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="builderagreement",
            name="website_contact_last_name",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="builderagreement",
            name="website_contact_phone_number",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="builderagreement",
            name="website_contact_title",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="historicalbuilderagreement",
            name="agreement_expiration_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="historicalbuilderagreement",
            name="agreement_start_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="historicalbuilderagreement",
            name="data",
            field=axis.core.fields.AxisJSONField(
                blank=True, default=dict, encoder=axis.core.fields.AxisJSONEncoder
            ),
        ),
        migrations.AlterField(
            model_name="historicalbuilderagreement",
            name="marketing_contact_cell_number",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="historicalbuilderagreement",
            name="marketing_contact_email_address",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="historicalbuilderagreement",
            name="marketing_contact_first_name",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="historicalbuilderagreement",
            name="marketing_contact_last_name",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="historicalbuilderagreement",
            name="marketing_contact_phone_number",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="historicalbuilderagreement",
            name="marketing_contact_title",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="historicalbuilderagreement",
            name="payment_contact_cell_number",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="historicalbuilderagreement",
            name="payment_contact_email_address",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="historicalbuilderagreement",
            name="payment_contact_first_name",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="historicalbuilderagreement",
            name="payment_contact_last_name",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="historicalbuilderagreement",
            name="payment_contact_phone_number",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="historicalbuilderagreement",
            name="payment_contact_title",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="historicalbuilderagreement",
            name="primary_contact_cell_number",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="historicalbuilderagreement",
            name="primary_contact_email_address",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="historicalbuilderagreement",
            name="primary_contact_first_name",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="historicalbuilderagreement",
            name="primary_contact_last_name",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="historicalbuilderagreement",
            name="primary_contact_phone_number",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="historicalbuilderagreement",
            name="primary_contact_title",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="historicalbuilderagreement",
            name="secondary_contact_cell_number",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="historicalbuilderagreement",
            name="secondary_contact_email_address",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="historicalbuilderagreement",
            name="secondary_contact_first_name",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="historicalbuilderagreement",
            name="secondary_contact_last_name",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="historicalbuilderagreement",
            name="secondary_contact_phone_number",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="historicalbuilderagreement",
            name="secondary_contact_title",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="historicalbuilderagreement",
            name="signer_email",
            field=models.EmailField(
                blank=True,
                help_text="Using for direct DocuSign workflow without AXIS User",
                max_length=254,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="historicalbuilderagreement",
            name="signer_name",
            field=models.CharField(
                blank=True,
                help_text="Using for direct DocuSign workflow without AXIS User",
                max_length=100,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="historicalbuilderagreement",
            name="website",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="historicalbuilderagreement",
            name="website_contact_cell_number",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="historicalbuilderagreement",
            name="website_contact_email_address",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="historicalbuilderagreement",
            name="website_contact_first_name",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="historicalbuilderagreement",
            name="website_contact_last_name",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="historicalbuilderagreement",
            name="website_contact_phone_number",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="historicalbuilderagreement",
            name="website_contact_title",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="historicalverifieragreement",
            name="agreement_expiration_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="historicalverifieragreement",
            name="agreement_start_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="historicalverifieragreement",
            name="applicant_email",
            field=models.EmailField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="historicalverifieragreement",
            name="applicant_first_name",
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AlterField(
            model_name="historicalverifieragreement",
            name="applicant_last_name",
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AlterField(
            model_name="historicalverifieragreement",
            name="applicant_phone_number",
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AlterField(
            model_name="historicalverifieragreement",
            name="applicant_title",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="historicalverifieragreement",
            name="hirl_agreement_docusign_data",
            field=axis.core.fields.AxisJSONField(
                blank=True, default=dict, encoder=axis.core.fields.AxisJSONEncoder
            ),
        ),
        migrations.AlterField(
            model_name="historicalverifieragreement",
            name="officer_agreement_docusign_data",
            field=axis.core.fields.AxisJSONField(
                blank=True, default=dict, encoder=axis.core.fields.AxisJSONEncoder
            ),
        ),
        migrations.AlterField(
            model_name="historicalverifieragreement",
            name="owner",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="company.company",
            ),
        ),
        migrations.AlterField(
            model_name="historicalverifieragreement",
            name="verifier",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="historicalverifieragreement",
            name="verifier_agreement_docusign_data",
            field=axis.core.fields.AxisJSONField(
                blank=True, default=dict, encoder=axis.core.fields.AxisJSONEncoder
            ),
        ),
        migrations.AlterField(
            model_name="verifieragreement",
            name="agreement_expiration_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="verifieragreement",
            name="agreement_start_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="verifieragreement",
            name="applicant_email",
            field=models.EmailField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="verifieragreement",
            name="applicant_first_name",
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AlterField(
            model_name="verifieragreement",
            name="applicant_last_name",
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AlterField(
            model_name="verifieragreement",
            name="applicant_phone_number",
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AlterField(
            model_name="verifieragreement",
            name="applicant_title",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="verifieragreement",
            name="hirl_agreement_docusign_data",
            field=axis.core.fields.AxisJSONField(
                blank=True, default=dict, encoder=axis.core.fields.AxisJSONEncoder
            ),
        ),
        migrations.AlterField(
            model_name="verifieragreement",
            name="hirl_certifying_document",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="filehandling.customerdocument",
            ),
        ),
        migrations.AlterField(
            model_name="verifieragreement",
            name="hirl_signed_agreement",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="filehandling.customerdocument",
            ),
        ),
        migrations.AlterField(
            model_name="verifieragreement",
            name="mailing_geocode",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="geocoder.geocode",
            ),
        ),
        migrations.AlterField(
            model_name="verifieragreement",
            name="officer_agreement_docusign_data",
            field=axis.core.fields.AxisJSONField(
                blank=True, default=dict, encoder=axis.core.fields.AxisJSONEncoder
            ),
        ),
        migrations.AlterField(
            model_name="verifieragreement",
            name="officer_certifying_document",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="filehandling.customerdocument",
            ),
        ),
        migrations.AlterField(
            model_name="verifieragreement",
            name="officer_signed_agreement",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="filehandling.customerdocument",
            ),
        ),
        migrations.AlterField(
            model_name="verifieragreement",
            name="owner",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="%(app_label)s_managed_verifier_agreements",
                to="company.company",
            ),
        ),
        migrations.AlterField(
            model_name="verifieragreement",
            name="shipping_geocode",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="geocoder.geocode",
            ),
        ),
        migrations.AlterField(
            model_name="verifieragreement",
            name="verifier",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="%(app_label)s_enrolled_verifier_agreements",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="verifieragreement",
            name="verifier_agreement_docusign_data",
            field=axis.core.fields.AxisJSONField(
                blank=True, default=dict, encoder=axis.core.fields.AxisJSONEncoder
            ),
        ),
        migrations.AlterField(
            model_name="verifieragreement",
            name="verifier_certifying_document",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="filehandling.customerdocument",
            ),
        ),
        migrations.AlterField(
            model_name="verifieragreement",
            name="verifier_signed_agreement",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="filehandling.customerdocument",
            ),
        ),
    ]