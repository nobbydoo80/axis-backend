# Generated by Django 3.1.8 on 2021-05-11 19:01

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0032_contactcard"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="contactcard",
            name="protected",
        ),
        migrations.AddField(
            model_name="contactcard",
            name="tag",
            field=models.CharField(
                blank=True,
                help_text="System field. Helps to identify field for related model that needs to be updated",
                max_length=255,
            ),
        ),
    ]
