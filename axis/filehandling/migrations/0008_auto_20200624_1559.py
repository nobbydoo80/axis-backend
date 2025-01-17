# Generated by Django 1.11.26 on 2020-06-24 15:59

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("filehandling", "0007_auto_20200415_1542"),
    ]

    operations = [
        migrations.AlterField(
            model_name="asynchronousprocesseddocument",
            name="final_status",
            field=models.CharField(
                choices=[
                    ("SUCCESS", "SUCCESS"),
                    ("FAILURE", "FAILURE"),
                    ("REVOKED", "REVOKED"),
                    ("STARTED", "STARTED"),
                    ("RETRY", "RETRY"),
                    ("RECEIVED", "RECEIVED"),
                    ("PENDING", "PENDING"),
                    ("UNACKNOWLEDGED", "UNACKNOWLEDGED"),
                ],
                max_length=50,
                null=True,
            ),
        ),
    ]
