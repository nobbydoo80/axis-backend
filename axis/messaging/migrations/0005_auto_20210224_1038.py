# Generated by Django 3.1.6 on 2021-02-24 10:38

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("messaging", "0004_auto_20201230_1218"),
    ]

    operations = [
        migrations.AlterField(
            model_name="message",
            name="sticky_alert",
            field=models.BooleanField(default=False, help_text="Stay visible until dismissed"),
        ),
    ]
