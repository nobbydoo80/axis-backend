# Generated by Django 4.0.8 on 2023-01-04 21:43

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("filehandling", "0012_alter_customerdocument_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="customerdocument",
            name="login_required",
            field=models.BooleanField(
                default=True, help_text="Allows document to be pulled without login"
            ),
        ),
        migrations.AddField(
            model_name="historicalcustomerdocument",
            name="login_required",
            field=models.BooleanField(
                default=True, help_text="Allows document to be pulled without login"
            ),
        ),
    ]
