# Generated by Django 4.0.7 on 2022-10-11 13:48

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("scheduling", "0016_auto_20221010_1749"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="historicaltask",
            name="content_type",
        ),
        migrations.RemoveField(
            model_name="historicaltask",
            name="home_address",
        ),
        migrations.RemoveField(
            model_name="historicaltask",
            name="object_id",
        ),
        migrations.RemoveField(
            model_name="task",
            name="content_type",
        ),
        migrations.RemoveField(
            model_name="task",
            name="home_address",
        ),
        migrations.RemoveField(
            model_name="task",
            name="object_id",
        ),
    ]