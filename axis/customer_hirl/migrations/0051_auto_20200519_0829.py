# Generated by Django 1.11.26 on 2020-05-19 08:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("customer_hirl", "0050_auto_20200518_1831"),
    ]

    operations = [
        migrations.AlterField(
            model_name="verifieragreement",
            name="verifier",
            field=models.OneToOneField(
                editable=False,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="customer_hirl_enrolled_verifier_agreement",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
