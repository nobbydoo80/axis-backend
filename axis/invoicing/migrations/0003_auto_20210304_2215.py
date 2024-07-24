# Generated by Django 3.1.6 on 2021-03-04 22:15

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("invoicing", "0002_auto_20210304_1946"),
    ]

    operations = [
        migrations.AlterField(
            model_name="historicalinvoice",
            name="id",
            field=models.UUIDField(db_index=True, default=uuid.uuid4, editable=False),
        ),
        migrations.AlterField(
            model_name="invoice",
            name="id",
            field=models.UUIDField(
                default=uuid.uuid4, editable=False, primary_key=True, serialize=False
            ),
        ),
    ]