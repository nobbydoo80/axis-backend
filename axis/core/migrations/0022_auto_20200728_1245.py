# Generated by Django 2.2 on 2020-07-28 12:45

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0021_auto_20200708_0838"),
    ]

    operations = [
        migrations.AlterField(
            model_name="historicaluser",
            name="last_name",
            field=models.CharField(blank=True, max_length=150, verbose_name="last name"),
        ),
        migrations.AlterField(
            model_name="user",
            name="last_name",
            field=models.CharField(blank=True, max_length=150, verbose_name="last name"),
        ),
    ]
