# Generated by Django 1.11.26 on 2020-06-19 17:44

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("annotation", "0004_auto_20190826_2024"),
    ]

    operations = [
        migrations.AlterField(
            model_name="type",
            name="slug",
            field=models.SlugField(editable=False, max_length=255, unique=True),
        ),
    ]
