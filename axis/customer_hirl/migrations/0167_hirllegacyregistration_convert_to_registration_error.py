# Generated by Django 3.1.8 on 2021-05-27 17:30

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("customer_hirl", "0166_auto_20210526_2108"),
    ]

    operations = [
        migrations.AddField(
            model_name="hirllegacyregistration",
            name="convert_to_registration_error",
            field=models.TextField(blank=True),
        ),
    ]
