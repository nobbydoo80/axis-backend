# Generated by Django 3.1.6 on 2021-02-12 20:17

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("customer_hirl", "0129_auto_20210212_1712"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="hirlproject",
            options={
                "ordering": ["-id"],
                "verbose_name": "Project",
                "verbose_name_plural": "Projects",
            },
        ),
    ]
