# Generated by Django 3.1.6 on 2021-04-13 12:23

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("customer_hirl", "0143_auto_20210409_1351"),
    ]

    operations = [
        migrations.AddField(
            model_name="hirlproject",
            name="lot_number",
            field=models.CharField(blank=True, max_length=16, null=True),
        ),
        migrations.AddField(
            model_name="historicalhirlproject",
            name="lot_number",
            field=models.CharField(blank=True, max_length=16, null=True),
        ),
    ]
