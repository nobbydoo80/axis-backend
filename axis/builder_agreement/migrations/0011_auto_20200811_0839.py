# Generated by Django 2.2 on 2020-08-11 08:39

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("builder_agreement", "0010_auto_20190826_2024"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="builderagreement",
            options={
                "ordering": (
                    "subdivision__name",
                    "subdivision__community__name",
                    "builder_org__name",
                ),
                "verbose_name": "Builder Agreement",
            },
        ),
    ]
