# Generated by Django 1.11.26 on 2020-04-15 15:40

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("user_management", "0026_inspectiongrade_qa_status"),
    ]

    operations = [
        migrations.AlterField(
            model_name="training",
            name="certificate",
            field=models.FileField(blank=True, null=True, upload_to="", verbose_name="Certificate"),
        ),
    ]
