# Generated by Django 4.0.8 on 2022-12-29 22:05

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("geographic", "0006_auto_20220719_1459"),
    ]

    operations = [
        migrations.AlterField(
            model_name="place",
            name="lot_number",
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
    ]