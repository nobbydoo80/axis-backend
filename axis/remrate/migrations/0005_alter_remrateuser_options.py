# Generated by Django 4.0.7 on 2022-09-14 18:47

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("remrate", "0004_auto_20220207_2050"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="remrateuser",
            options={"ordering": ("username",), "verbose_name": "REM/Rate User"},
        ),
    ]
