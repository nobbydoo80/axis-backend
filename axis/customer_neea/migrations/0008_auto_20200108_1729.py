# Generated by Django 1.11.26 on 2020-01-08 17:29

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("customer_neea", "0007_auto_20200108_1658"),
    ]

    operations = [
        migrations.RenameField(
            model_name="neeacertification",
            old_name="date_registered",
            new_name="certification_date",
        ),
    ]