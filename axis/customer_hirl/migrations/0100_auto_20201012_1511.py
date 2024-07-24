# Generated by Django 2.2 on 2020-10-12 15:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("customer_hirl", "0099_auto_20201012_1509"),
    ]

    operations = [
        migrations.AlterField(
            model_name="verifieragreement",
            name="verifier",
            field=models.ForeignKey(
                editable=False,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="customer_hirl_enrolled_verifier_agreements",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
