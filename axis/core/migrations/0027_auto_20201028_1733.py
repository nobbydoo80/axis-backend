# Generated by Django 2.2 on 2020-10-28 17:33

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0026_recentlyviewed"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="recentlyviewed",
            name="created_at",
        ),
        migrations.AddField(
            model_name="recentlyviewed",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
    ]
