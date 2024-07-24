# Generated by Django 1.11.26 on 2020-04-16 13:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_fsm
import simple_history.models


class Migration(migrations.Migration):
    dependencies = [
        ("company", "0005_auto_20200401_1357"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("customer_hirl", "0021_auto_20200128_1940"),
    ]

    operations = [
        migrations.CreateModel(
            name="HistoricalVerifierAgreement",
            fields=[
                (
                    "id",
                    models.IntegerField(
                        auto_created=True, blank=True, db_index=True, verbose_name="ID"
                    ),
                ),
                (
                    "state",
                    django_fsm.FSMField(
                        choices=[("new", "Submitted"), ("approved", "Approved")],
                        default="new",
                        max_length=50,
                        protected=True,
                    ),
                ),
                ("date_created", models.DateTimeField(blank=True, editable=False)),
                ("date_modified", models.DateTimeField(blank=True, editable=False)),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_date", models.DateTimeField()),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                (
                    "history_type",
                    models.CharField(
                        choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")], max_length=1
                    ),
                ),
                (
                    "company",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="company.Company",
                    ),
                ),
                (
                    "history_user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="company.Company",
                    ),
                ),
            ],
            options={
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": "history_date",
                "verbose_name": "historical verifier agreement",
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="VerifierAgreement",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "state",
                    django_fsm.FSMField(
                        choices=[("new", "Submitted"), ("approved", "Approved")],
                        default="new",
                        max_length=50,
                        protected=True,
                    ),
                ),
                ("date_created", models.DateTimeField(auto_now_add=True)),
                ("date_modified", models.DateTimeField(auto_now=True)),
                (
                    "company",
                    models.ForeignKey(
                        editable=False,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="customer_hirl_enrolled_verifier_agreements",
                        to="company.Company",
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        editable=False,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="customer_hirl_managed_verifier_agreements",
                        to="company.Company",
                    ),
                ),
            ],
            options={
                "permissions": (("view_verifieragreement", "View Verifier Agreement"),),
            },
        ),
    ]
