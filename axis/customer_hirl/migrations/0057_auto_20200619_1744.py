# Generated by Django 1.11.26 on 2020-06-19 17:44

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("customer_hirl", "0056_hirlraterorganization"),
    ]

    operations = [
        migrations.AlterField(
            model_name="coidocument",
            name="document",
            field=models.FileField(max_length=512, upload_to=""),
        ),
    ]