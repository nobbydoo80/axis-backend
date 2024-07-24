# Generated by Django 1.11.16 on 2018-10-08 18:15

import axis.core.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("company", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("checklist", "0002_auto_20181008_1815"),
        ("home", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="HistoricalSampleSet",
            fields=[
                (
                    "id",
                    models.IntegerField(
                        auto_created=True, blank=True, db_index=True, verbose_name="ID"
                    ),
                ),
                (
                    "uuid",
                    axis.core.fields.UUIDField(
                        blank=True, db_index=True, editable=False, max_length=64
                    ),
                ),
                ("alt_name", models.CharField(blank=True, max_length=32, null=True)),
                ("start_date", models.DateField(blank=True, editable=False)),
                ("confirm_date", models.DateField(blank=True, null=True)),
                ("revision", models.PositiveIntegerField(default=0)),
                (
                    "is_metro_sampled",
                    models.BooleanField(
                        default=False,
                        help_text="Tracks last known state of this flag as calculated by its member homestatuses.",
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
                "verbose_name": "historical sample set",
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="HistoricalSamplingProviderApproval",
            fields=[
                (
                    "id",
                    models.IntegerField(
                        auto_created=True, blank=True, db_index=True, verbose_name="ID"
                    ),
                ),
                ("sampling_approved", models.BooleanField(default=False, verbose_name="Approved")),
                ("created_date", models.DateTimeField(blank=True, editable=False)),
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
                    "history_user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "provider",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="company.ProviderOrganization",
                    ),
                ),
                (
                    "target",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
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
                "verbose_name": "historical sampling provider approval",
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="SampleSet",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "uuid",
                    axis.core.fields.UUIDField(
                        blank=True, editable=False, max_length=64, unique=True
                    ),
                ),
                ("alt_name", models.CharField(blank=True, max_length=32, null=True)),
                ("start_date", models.DateField(auto_now_add=True)),
                ("confirm_date", models.DateField(blank=True, null=True)),
                ("revision", models.PositiveIntegerField(default=0)),
                (
                    "is_metro_sampled",
                    models.BooleanField(
                        default=False,
                        help_text="Tracks last known state of this flag as calculated by its member homestatuses.",
                    ),
                ),
            ],
            options={
                "ordering": ("uuid",),
            },
        ),
        migrations.CreateModel(
            name="SampleSetHomeStatus",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("created_date", models.DateTimeField(auto_now_add=True)),
                ("modified_date", models.DateTimeField(auto_now=True)),
                ("revision", models.PositiveIntegerField()),
                ("is_active", models.BooleanField(default=False)),
                (
                    "is_test_home",
                    models.BooleanField(
                        default=False,
                        help_text="Indicates whether this home is providing answers or receiving them.",
                    ),
                ),
                ("answers", models.ManyToManyField(blank=True, to="checklist.Answer")),
                (
                    "home_status",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="home.EEPProgramHomeStatus"
                    ),
                ),
                (
                    "sampleset",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="sampleset.SampleSet"
                    ),
                ),
            ],
            options={
                "verbose_name": "Sample Set Home Status",
                "verbose_name_plural": "Sample Set Home Statuses",
            },
        ),
        migrations.CreateModel(
            name="SamplingProviderApproval",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("sampling_approved", models.BooleanField(default=False, verbose_name="Approved")),
                ("created_date", models.DateTimeField(auto_now_add=True)),
                (
                    "provider",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sampling_approver",
                        to="company.ProviderOrganization",
                    ),
                ),
                (
                    "target",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sampling_approved",
                        to="company.Company",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Provider Sampling Approvals",
            },
        ),
        migrations.AddField(
            model_name="sampleset",
            name="home_statuses",
            field=models.ManyToManyField(
                through="sampleset.SampleSetHomeStatus", to="home.EEPProgramHomeStatus"
            ),
        ),
        migrations.AddField(
            model_name="sampleset",
            name="owner",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="owned_samplesets",
                to="company.Company",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="samplesethomestatus",
            unique_together=set([("sampleset", "home_status", "revision")]),
        ),
    ]
