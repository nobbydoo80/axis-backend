# Generated by Django 3.2.9 on 2021-11-19 11:23

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("customer_hirl", "0194_auto_20211119_1120"),
    ]

    operations = [
        migrations.AlterField(
            model_name="hirlrateruser",
            name="hirl_id",
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
