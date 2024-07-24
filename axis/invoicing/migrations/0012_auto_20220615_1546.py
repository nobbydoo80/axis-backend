# Generated by Django 3.2.13 on 2022-06-15 15:46

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("invoicing", "0011_auto_20211220_1205"),
    ]

    operations = [
        migrations.AddField(
            model_name="historicalinvoice",
            name="total",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                help_text="Field automatically updating based on InvoiceItem sum cost",
                max_digits=16,
            ),
        ),
        migrations.AddField(
            model_name="historicalinvoice",
            name="total_paid",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                help_text="Field automatically updating based on InvoiceItemTransaction sum amount",
                max_digits=16,
            ),
        ),
        migrations.AddField(
            model_name="invoice",
            name="total",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                help_text="Field automatically updating based on InvoiceItem sum cost",
                max_digits=16,
            ),
        ),
        migrations.AddField(
            model_name="invoice",
            name="total_paid",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                help_text="Field automatically updating based on InvoiceItemTransaction sum amount",
                max_digits=16,
            ),
        ),
    ]