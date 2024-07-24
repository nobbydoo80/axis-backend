# Generated by Django 2.2 on 2020-10-16 14:44

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("user_management", "0030_auto_20200714_1352"),
    ]

    operations = [
        migrations.AlterField(
            model_name="accreditation",
            name="accreditation_cycle",
            field=models.SmallIntegerField(
                choices=[
                    (1, "Annual"),
                    (2, "Every 2 years"),
                    (3, "Every 3 years"),
                    (4, "Every 4 years"),
                ],
                default=1,
                verbose_name="Accreditation Cycle",
            ),
        ),
    ]