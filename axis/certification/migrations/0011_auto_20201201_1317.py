# Generated by Django 2.2 on 2020-12-01 13:17

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("certification", "0010_auto_20201112_1154"),
    ]

    operations = [
        migrations.AlterField(
            model_name="workflow",
            name="config_path",
            field=models.FilePathField(
                allow_folders=True,
                match="^[^_].*(?<!\\.pyc)$",
                path="/Users/artemhruzd/Development/Pivotal/axis/axis/certification/configs",
            ),
        ),
    ]
