# Generated by Django 1.11.26 on 2020-02-13 07:04

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("eep_program", "0016_resnet_registry_data"),
        ("user_management", "0019_training_certificate"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="accreditation",
            name="accreditation_program",
        )
    ]