# Generated by Django 2.2 on 2020-10-02 15:59

import axis.core.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("customer_hirl", "0087_auto_20201001_1034"),
    ]

    operations = [
        migrations.CreateModel(
            name="HIRLVerifierAgreementStatus",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("data", axis.core.fields.AxisJSONField(default=dict)),
                ("hirl_id", models.PositiveIntegerField(verbose_name="Internal ID")),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "hirl_verifier_agreement",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="customer_hirl.VerifierAgreement",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="HIRLBuilderAgreementStatus",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("data", axis.core.fields.AxisJSONField(default=dict)),
                ("hirl_id", models.PositiveIntegerField(verbose_name="Internal ID")),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "hirl_builder_agreement",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="customer_hirl.BuilderAgreement",
                    ),
                ),
            ],
        ),
    ]
