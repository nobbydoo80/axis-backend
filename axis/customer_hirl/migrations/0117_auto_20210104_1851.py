# Generated by Django 3.1.3 on 2021-01-04 18:51

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("customer_hirl", "0116_auto_20210104_1610"),
    ]

    operations = [
        migrations.RenameField(
            model_name="hirlprojectarchitect",
            old_name="community_architects_organization",
            new_name="architect_organization",
        ),
        migrations.RenameField(
            model_name="hirlprojectdeveloper",
            old_name="community_developer_owner_organization",
            new_name="developer_organization",
        ),
    ]
