# Generated by Django 1.11.17 on 2019-11-01 11:45

from django.db import migrations, models
import django.db.models.deletion
import django_fsm


class Migration(migrations.Migration):
    dependencies = [
        ("equipment", "0005_auto_20191030_1957"),
    ]

    operations = [
        migrations.AlterField(
            model_name="equipment",
            name="owner_company",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="equipments",
                to="company.Company",
            ),
        ),
        migrations.AlterField(
            model_name="equipmentsponsorstatus",
            name="state",
            field=django_fsm.FSMField(
                choices=[
                    ("new", "New"),
                    ("active", "Active"),
                    ("rejected", "Rejected"),
                    ("expired", "Expired"),
                ],
                default="new",
                max_length=50,
            ),
        ),
    ]
