# Generated by Django 3.1.3 on 2021-01-15 16:23

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("customer_hirl", "0124_auto_20210113_1743"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="hirlgreenenergybadge",
            options={
                "ordering": ("name",),
                "verbose_name": "Green Energy Badge",
                "verbose_name_plural": "Green Energy Badges",
            },
        ),
        migrations.AlterModelOptions(
            name="hirlresponsiblename",
            options={
                "ordering": ("name",),
                "verbose_name": "Responsible Name",
                "verbose_name_plural": "Responsible Names",
            },
        ),
        migrations.AlterField(
            model_name="hirlproject",
            name="multi_family_project_name",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name="historicalhirlproject",
            name="multi_family_project_name",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]