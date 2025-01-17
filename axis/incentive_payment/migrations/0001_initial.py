# Generated by Django 1.11.16 on 2018-10-08 18:15

import axis.core.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_states.fields
import simple_history.models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("company", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("home", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="HistoricalIncentiveDistribution",
            fields=[
                (
                    "id",
                    models.IntegerField(
                        auto_created=True, blank=True, db_index=True, verbose_name="ID"
                    ),
                ),
                ("check_to_name", models.CharField(max_length=64, null=True)),
                ("invoice_number", models.CharField(blank=True, max_length=64, null=True)),
                ("check_requested", models.BooleanField(default=False)),
                ("check_requested_date", models.DateField(null=True)),
                ("is_paid", models.BooleanField(default=False)),
                ("paid_date", models.DateField(blank=True, null=True)),
                ("check_number", models.CharField(blank=True, max_length=24, null=True)),
                (
                    "status",
                    models.IntegerField(
                        choices=[(1, "Check Requested"), (2, "Paid"), (3, "Refund")]
                    ),
                ),
                (
                    "total",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        help_text="Automatically filled in from sum tasks and expenses on save.",
                        max_digits=8,
                    ),
                ),
                ("comment", models.TextField(blank=True, null=True)),
                (
                    "slug",
                    axis.core.fields.UUIDField(
                        blank=True, db_index=True, editable=False, max_length=64
                    ),
                ),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                ("history_date", models.DateTimeField()),
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
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="company.Company",
                    ),
                ),
                (
                    "customer",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
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
            ],
            options={
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": "history_date",
                "verbose_name": "historical Incentive Payment",
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="IncentiveDistribution",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("check_to_name", models.CharField(max_length=64, null=True)),
                ("invoice_number", models.CharField(blank=True, max_length=64, null=True)),
                ("check_requested", models.BooleanField(default=False)),
                ("check_requested_date", models.DateField(null=True)),
                ("is_paid", models.BooleanField(default=False)),
                ("paid_date", models.DateField(blank=True, null=True)),
                ("check_number", models.CharField(blank=True, max_length=24, null=True)),
                (
                    "status",
                    models.IntegerField(
                        choices=[(1, "Check Requested"), (2, "Paid"), (3, "Refund")]
                    ),
                ),
                (
                    "total",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        help_text="Automatically filled in from sum tasks and expenses on save.",
                        max_digits=8,
                    ),
                ),
                ("comment", models.TextField(blank=True, null=True)),
                (
                    "slug",
                    axis.core.fields.UUIDField(
                        blank=True, editable=False, max_length=64, unique=True
                    ),
                ),
                (
                    "company",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="eep_sponsor",
                        to="company.Company",
                    ),
                ),
                (
                    "customer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="eep_recipient",
                        to="company.Company",
                    ),
                ),
                (
                    "rater_incentives",
                    models.ManyToManyField(
                        blank=True,
                        related_name="parent_incentive_distributions",
                        to="incentive_payment.IncentiveDistribution",
                    ),
                ),
            ],
            options={"ordering": ["invoice_number"], "verbose_name": "Incentive Payment"},
        ),
        migrations.CreateModel(
            name="IncentivePaymentStatus",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("created_on", models.DateTimeField(editable=False)),
                ("last_update", models.DateTimeField()),
                (
                    "state",
                    django_states.fields.StateField(
                        default=b"start", max_length=100, verbose_name="state id"
                    ),
                ),
                (
                    "home_status",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE, to="home.EEPProgramHomeStatus"
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="company.Company"
                    ),
                ),
            ],
            options={
                "verbose_name": "Incentive Payment Status",
                "verbose_name_plural": "Incentive Payment Statuses",
            },
        ),
        migrations.CreateModel(
            name="IncentivePaymentStatusStateLog",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "state",
                    django_states.fields.StateField(
                        default=b"transition_initiated", max_length=100, verbose_name="state id"
                    ),
                ),
                (
                    "from_state",
                    models.CharField(
                        choices=[
                            ("start", "Received"),
                            ("ipp_payment_requirements", "Approved"),
                            ("ipp_payment_automatic_requirements", "Approved for Payment"),
                            ("payment_pending", "Payment Pending"),
                            ("complete", "Paid"),
                            ("ipp_payment_failed_requirements", "Correction Required"),
                            ("ipp_failed_restart", "Correction Received"),
                        ],
                        max_length=100,
                    ),
                ),
                (
                    "to_state",
                    models.CharField(
                        choices=[
                            ("start", "Received"),
                            ("ipp_payment_requirements", "Approved"),
                            ("ipp_payment_automatic_requirements", "Approved for Payment"),
                            ("payment_pending", "Payment Pending"),
                            ("complete", "Paid"),
                            ("ipp_payment_failed_requirements", "Correction Required"),
                            ("ipp_failed_restart", "Correction Received"),
                        ],
                        max_length=100,
                    ),
                ),
                ("serialized_kwargs", models.TextField(blank=True)),
                (
                    "start_time",
                    models.DateTimeField(
                        auto_now_add=True, db_index=True, verbose_name="transition started at"
                    ),
                ),
                (
                    "on",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="state_history",
                        to="incentive_payment.IncentivePaymentStatus",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Incentive Payment Status transition",
            },
        ),
        migrations.CreateModel(
            name="IPPItem",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("cost", models.DecimalField(decimal_places=2, default=0.0, max_digits=9)),
                (
                    "home_status",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="home.EEPProgramHomeStatus"
                    ),
                ),
                (
                    "incentive_distribution",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="incentive_payment.IncentiveDistribution",
                    ),
                ),
            ],
            options={"ordering": ["home_status__home"], "verbose_name": "Incentive Item"},
        ),
    ]
