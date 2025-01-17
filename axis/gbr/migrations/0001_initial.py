# Generated by Django 4.0.8 on 2023-01-18 22:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("home", "0026_alter_historicalhome_lot_number_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="HistoricalGreenBuildingRegistry",
            fields=[
                (
                    "id",
                    models.BigIntegerField(
                        auto_created=True, blank=True, db_index=True, verbose_name="ID"
                    ),
                ),
                ("gbr_id", models.CharField(max_length=32, null=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("Not yet started", "Not Started"),
                            ("Imported from HES HPXML", "Legacy Import"),
                            ("Address created and valid", "Property Valid"),
                            ("Address creation failed", "Property Invalid"),
                            ("Assessment Created", "Assessment Created"),
                            ("Assessment Creation Failed", "Assessment Invalid"),
                        ],
                        default="Not yet started",
                        max_length=32,
                    ),
                ),
                ("api_result", models.JSONField(null=True)),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_date", models.DateTimeField(db_index=True)),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
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
                    "home",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="home.home",
                    ),
                ),
            ],
            options={
                "verbose_name": "historical Green Building Registry Entry",
                "verbose_name_plural": "historical Green Building Registry Entries",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="GreenBuildingRegistry",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("gbr_id", models.CharField(max_length=32, null=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("Not yet started", "Not Started"),
                            ("Imported from HES HPXML", "Legacy Import"),
                            ("Address created and valid", "Property Valid"),
                            ("Address creation failed", "Property Invalid"),
                            ("Assessment Created", "Assessment Created"),
                            ("Assessment Creation Failed", "Assessment Invalid"),
                        ],
                        default="Not yet started",
                        max_length=32,
                    ),
                ),
                ("api_result", models.JSONField(null=True)),
                (
                    "home",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="gbr",
                        to="home.home",
                    ),
                ),
            ],
            options={
                "verbose_name": "Green Building Registry Entry",
                "verbose_name_plural": "Green Building Registry Entries",
                "ordering": ("gbr_id",),
            },
        ),
    ]
