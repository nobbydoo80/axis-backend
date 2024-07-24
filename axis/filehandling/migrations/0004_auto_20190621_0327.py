# Generated by Django 1.11.17 on 2019-06-21 03:27

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("filehandling", "0003_auto_20190531_1224"),
    ]

    operations = [
        migrations.AlterField(
            model_name="asynchronousprocesseddocument",
            name="final_status",
            field=models.CharField(
                choices=[
                    ("FAILURE", "FAILURE"),
                    ("RETRY", "RETRY"),
                    ("REVOKED", "REVOKED"),
                    ("SUCCESS", "SUCCESS"),
                    ("RECEIVED", "RECEIVED"),
                    ("STARTED", "STARTED"),
                    ("UNACKNOWLEDGED", "UNACKNOWLEDGED"),
                    ("PENDING", "PENDING"),
                ],
                max_length=50,
                null=True,
            ),
        ),
    ]