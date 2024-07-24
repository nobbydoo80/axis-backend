# Generated by Django 4.0.7 on 2022-08-25 17:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("customer_hirl", "0209_remove_hirlproject_is_build_to_rent_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="builderagreement",
            name="initiator",
            field=models.ForeignKey(
                blank=True,
                help_text="User from other company(mostly Verifier) who created this Client Agreement for Company",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="%(app_label)s_initiated_client_agreements",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="historicalbuilderagreement",
            name="initiator",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                help_text="User from other company(mostly Verifier) who created this Client Agreement for Company",
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="builderagreement",
            name="signer_email",
            field=models.EmailField(
                help_text="Using for direct DocuSign workflow without AXIS User",
                max_length=254,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="historicalbuilderagreement",
            name="signer_email",
            field=models.EmailField(
                help_text="Using for direct DocuSign workflow without AXIS User",
                max_length=254,
                null=True,
            ),
        ),
    ]
