# Generated by Django 3.1.3 on 2021-01-15 16:27

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("company", "0021_auto_20210104_1942"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="altname",
            options={"ordering": ("name",), "verbose_name": "Alternative Name"},
        ),
        migrations.AlterModelOptions(
            name="architectorganization",
            options={
                "ordering": ("name",),
                "verbose_name_plural": "Community Architects Companies",
            },
        ),
        migrations.AlterModelOptions(
            name="builderorganization",
            options={"ordering": ("name",), "verbose_name": "Builder"},
        ),
        migrations.AlterModelOptions(
            name="communityownerorganization",
            options={"ordering": ("name",), "verbose_name_plural": "Community Developer Companies"},
        ),
        migrations.AlterModelOptions(
            name="developerorganization",
            options={
                "ordering": ("name",),
                "verbose_name_plural": "Community Developer Owner Companies",
            },
        ),
        migrations.AlterModelOptions(
            name="eeporganization",
            options={"ordering": ("name",), "verbose_name": "Program Sponsor"},
        ),
        migrations.AlterModelOptions(
            name="hvacorganization",
            options={
                "ordering": ("name",),
                "verbose_name": "HVAC Company",
                "verbose_name_plural": "HVAC Companies",
            },
        ),
        migrations.AlterModelOptions(
            name="providerorganization",
            options={"ordering": ("name",), "verbose_name": "Provider"},
        ),
        migrations.AlterModelOptions(
            name="qaorganization",
            options={"ordering": ("name",), "verbose_name_plural": "QA/QC Companies"},
        ),
        migrations.AlterModelOptions(
            name="raterorganization",
            options={
                "ordering": ("name",),
                "verbose_name": "Rating Company",
                "verbose_name_plural": "Rating Companies",
            },
        ),
        migrations.AlterModelOptions(
            name="utilityorganization",
            options={
                "ordering": ("name",),
                "verbose_name": "Utility Company",
                "verbose_name_plural": "Utility Companies",
            },
        ),
    ]
