# Generated by Django 1.11.17 on 2019-11-28 12:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Training",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("name", models.CharField(max_length=64)),
                (
                    "address",
                    models.CharField(help_text="Company/Conference location", max_length=255),
                ),
                (
                    "training_type",
                    models.PositiveSmallIntegerField(
                        choices=[(0, "Voluntary"), (1, "Mandatory")], default=0
                    ),
                ),
                (
                    "attendance_type",
                    models.PositiveSmallIntegerField(
                        choices=[(0, "In-person"), (1, "Remote"), (2, "ABSENT")], default=2
                    ),
                ),
                ("duration", models.DurationField()),
                ("notes", models.TextField(blank=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
                    ),
                ),
            ],
        ),
    ]
