# Generated by Django 3.1.3 on 2020-12-30 12:18

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("messaging", "0003_auto_20190305_1935"),
    ]

    operations = [
        migrations.AlterField(
            model_name="message",
            name="email_read",
            field=models.BooleanField(default=None, null=True),
        ),
    ]
