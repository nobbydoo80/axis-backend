# Generated by Django 4.0.8 on 2022-12-09 20:23

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("invoicing", "0016_remove_historicalinvoiceitemgroup_label_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="historicalinvoiceitemgroup",
            name="category",
            field=models.CharField(
                choices=[("", "Any"), ("appeals_fees", "Appeals Fees")], default="", max_length=255
            ),
        ),
        migrations.AlterField(
            model_name="invoiceitemgroup",
            name="category",
            field=models.CharField(
                choices=[("", "Any"), ("appeals_fees", "Appeals Fees")], default="", max_length=255
            ),
        ),
    ]
