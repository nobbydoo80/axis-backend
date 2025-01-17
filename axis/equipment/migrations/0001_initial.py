# Generated by Django 1.11.17 on 2019-10-29 18:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_fsm


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("company", "0004_auto_20190826_2024"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Equipment",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("equipment_type", models.CharField(max_length=255)),
                ("calibration_date", models.DateField()),
                ("calibration_cycle", models.CharField(max_length=255)),
                ("calibration_company", models.CharField(max_length=255)),
                ("brand", models.CharField(max_length=255)),
                ("model", models.CharField(max_length=255)),
                ("serial", models.CharField(max_length=255)),
                ("description", models.TextField()),
                ("notes", models.TextField()),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="owner_company",
                        to="company.Company",
                    ),
                ),
            ],
            options={
                "verbose_name": "Equipment",
                "verbose_name_plural": "Equipments",
            },
        ),
        migrations.CreateModel(
            name="EquipmentSponsorStatus",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("approve_date", models.DateField()),
                (
                    "state",
                    django_fsm.FSMField(
                        choices=[
                            ("new", "New"),
                            ("active", "Active"),
                            ("rejected", "Rejected"),
                            ("expired", "Expired"),
                        ],
                        default="new",
                        max_length=50,
                        protected=True,
                    ),
                ),
                (
                    "approver",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
                    ),
                ),
                (
                    "company",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="company.Company"
                    ),
                ),
                (
                    "equipment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="equipment.Equipment"
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="equipment",
            name="sponsors",
            field=models.ManyToManyField(
                through="equipment.EquipmentSponsorStatus", to="company.Company"
            ),
        ),
    ]
