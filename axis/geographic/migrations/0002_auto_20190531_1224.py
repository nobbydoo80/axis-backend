# Generated by Django 1.11.17 on 2019-05-31 12:24

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("geographic", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="place",
            name="created_date",
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
