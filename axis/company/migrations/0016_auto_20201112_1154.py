# Generated by Django 2.2 on 2020-11-12 11:54

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("company", "0015_auto_20201027_1829"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="sponsorpreferences",
            options={
                "ordering": ("sponsored_company__name",),
                "verbose_name_plural": "Sponsor preferences",
            },
        ),
    ]
