# Generated by Django 1.11.26 on 2020-05-15 09:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("company", "0008_auto_20200513_0909"),
        ("customer_hirl", "0044_auto_20200513_1050"),
    ]

    operations = [
        migrations.CreateModel(
            name="COIDocument",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("document", models.FileField(max_length=512, upload_to=b"")),
                ("filesize", models.PositiveIntegerField(blank=True, editable=False, null=True)),
                ("description", models.CharField(blank=True, max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("last_update", models.DateTimeField(auto_now=True)),
                (
                    "company",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="verifier_agreement_coi_documents",
                        to="company.Company",
                    ),
                ),
            ],
            options={"verbose_name": "COI Document"},
        ),
        migrations.CreateModel(
            name="HistoricalCOIDocument",
            fields=[
                (
                    "id",
                    models.IntegerField(
                        auto_created=True, blank=True, db_index=True, verbose_name="ID"
                    ),
                ),
                ("document", models.TextField(max_length=512)),
                ("filesize", models.PositiveIntegerField(blank=True, editable=False, null=True)),
                ("description", models.CharField(blank=True, max_length=255)),
                ("created_at", models.DateTimeField(blank=True, editable=False)),
                ("last_update", models.DateTimeField(blank=True, editable=False)),
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
                "verbose_name": "historical COI Document",
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]
