# Generated by Django 4.2.1 on 2023-05-22 07:54

from django.db import migrations, models
import django_fsm


class Migration(migrations.Migration):
    dependencies = [
        ("customer_hirl", "0234_builderagreement_extension_request_certifying_document_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="builderagreement",
            name="extension_request_reject_reason",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="historicalbuilderagreement",
            name="extension_request_reject_reason",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="builderagreement",
            name="extension_request_state",
            field=django_fsm.FSMField(
                choices=[
                    ("not_sent", "Not sent"),
                    ("initiated", "Initiated"),
                    ("sent_to_client", "Sent to Client"),
                    ("sent_for_countersigned", "Sent for Counter-Signing"),
                    ("countersigned", "Counter-Signed"),
                    ("rejected", "Rejected"),
                ],
                default="not_sent",
                help_text="State for extension request",
                max_length=50,
            ),
        ),
        migrations.AlterField(
            model_name="historicalbuilderagreement",
            name="extension_request_state",
            field=django_fsm.FSMField(
                choices=[
                    ("not_sent", "Not sent"),
                    ("initiated", "Initiated"),
                    ("sent_to_client", "Sent to Client"),
                    ("sent_for_countersigned", "Sent for Counter-Signing"),
                    ("countersigned", "Counter-Signed"),
                    ("rejected", "Rejected"),
                ],
                default="not_sent",
                help_text="State for extension request",
                max_length=50,
            ),
        ),
    ]