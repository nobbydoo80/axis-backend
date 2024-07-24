# Generated by Django 1.11.26 on 2019-12-05 11:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_fsm
import simple_history.models


class Migration(migrations.Migration):
    dependencies = [
        ("company", "0004_auto_20190826_2024"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("user_management", "0004_auto_20191203_2302"),
    ]

    operations = [
        migrations.CreateModel(
            name="Accreditation",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("rtin", models.CharField(max_length=255, verbose_name="ID/RTIN")),
                (
                    "certification_type",
                    models.SmallIntegerField(
                        choices=[(0, "Annual"), (1, "Every 2 years"), (2, "Every 3 years")],
                        default=0,
                    ),
                ),
                ("date_initial", models.DateField(blank=True, null=True)),
                ("date_last", models.DateField(blank=True, null=True)),
                ("role", models.TextField()),
                ("notes", models.TextField(blank=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="AccreditationStatus",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("state_changed_at", models.DateTimeField(blank=True, null=True)),
                (
                    "state",
                    django_fsm.FSMField(
                        choices=[
                            ("new", "New (Unapproved)"),
                            ("active", "Active"),
                            ("rejected", "Rejected"),
                            ("expired", "Expired"),
                        ],
                        default="new",
                        max_length=50,
                    ),
                ),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "accreditation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="user_management.Accreditation",
                    ),
                ),
                (
                    "approver",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "company",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="company.Company"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="HistoricalAccreditationStatus",
            fields=[
                (
                    "id",
                    models.IntegerField(
                        auto_created=True, blank=True, db_index=True, verbose_name="ID"
                    ),
                ),
                ("state_changed_at", models.DateTimeField(blank=True, null=True)),
                (
                    "state",
                    django_fsm.FSMField(
                        choices=[
                            ("new", "New (Unapproved)"),
                            ("active", "Active"),
                            ("rejected", "Rejected"),
                            ("expired", "Expired"),
                        ],
                        default="new",
                        max_length=50,
                    ),
                ),
                ("updated_at", models.DateTimeField(blank=True, editable=False)),
                ("created_at", models.DateTimeField(blank=True, editable=False)),
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
                    "accreditation",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="user_management.Accreditation",
                    ),
                ),
                (
                    "approver",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
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
                "verbose_name": "historical accreditation status",
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.AddField(
            model_name="accreditation",
            name="statuses",
            field=models.ManyToManyField(
                through="user_management.AccreditationStatus", to="company.Company"
            ),
        ),
        migrations.AddField(
            model_name="accreditation",
            name="trainee",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AlterUniqueTogether(
            name="accreditationstatus",
            unique_together=set([("accreditation", "company")]),
        ),
    ]