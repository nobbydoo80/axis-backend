# Generated by Django 3.1.8 on 2021-04-28 08:17

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("customer_hirl", "0153_merge_20210427_1616"),
    ]

    operations = [
        migrations.RenameField(
            model_name="hirlprojectregistration",
            old_name="multi_family_project_name",
            new_name="project_name",
        ),
        migrations.RenameField(
            model_name="historicalhirlprojectregistration",
            old_name="multi_family_project_name",
            new_name="project_name",
        ),
    ]
