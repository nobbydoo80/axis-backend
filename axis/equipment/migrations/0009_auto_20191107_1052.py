# Generated by Django 1.11.17 on 2019-11-07 10:52

from django.db import migrations, models
import django.db.models.deletion
import django_fsm


class Migration(migrations.Migration):
    dependencies = [
        ("equipment", "0008_auto_20191104_2138"),
    ]

    operations = [
        migrations.AddField(
            model_name="equipment",
            name="expired_equipment",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="equipment.Equipment",
            ),
        ),
        migrations.AlterField(
            model_name="equipmentsponsorstatus",
            name="state",
            field=django_fsm.FSMField(
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
    ]
