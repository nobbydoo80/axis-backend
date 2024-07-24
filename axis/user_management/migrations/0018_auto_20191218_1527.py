# Generated by Django 1.11.26 on 2019-12-18 15:27

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("user_management", "0017_auto_20191218_1418"),
    ]

    operations = [
        migrations.AlterField(
            model_name="inspectiongrade",
            name="grade",
            field=models.PositiveSmallIntegerField(
                choices=[(1, "A"), (2, "B"), (3, "C"), (4, "D"), (5, "F")], default=5
            ),
        ),
    ]
