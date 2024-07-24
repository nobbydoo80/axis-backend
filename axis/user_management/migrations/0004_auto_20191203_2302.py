# Generated by Django 1.11.26 on 2019-12-03 23:02

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("user_management", "0003_auto_20191203_1727"),
    ]

    operations = [
        migrations.AlterField(
            model_name="training",
            name="attendance_type",
            field=models.PositiveSmallIntegerField(
                choices=[(1, "In-person"), (2, "Remote"), (3, "ABSENT")], default=3
            ),
        ),
        migrations.AlterField(
            model_name="training",
            name="training_type",
            field=models.PositiveSmallIntegerField(
                choices=[(1, "Voluntary"), (2, "Mandatory")], default=2
            ),
        ),
    ]
