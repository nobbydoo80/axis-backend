# Generated by Django 1.11.16 on 2018-11-23 15:58

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ekotrope", "0002_auto_20181008_1816"),
    ]

    operations = [
        migrations.AlterField(
            model_name="analysis",
            name="import_request",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="houseplan",
            name="import_request",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="project",
            name="import_request",
            field=models.TextField(blank=True, null=True),
        ),
    ]