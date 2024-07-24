# Generated by Django 3.2.10 on 2021-12-20 12:05

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("invoicing", "0010_auto_20210707_1911"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="historicalinvoice",
            options={
                "get_latest_by": "history_date",
                "ordering": ("-history_date", "-history_id"),
                "verbose_name": "historical Invoice",
            },
        ),
        migrations.AlterModelOptions(
            name="historicalinvoiceitem",
            options={
                "get_latest_by": "history_date",
                "ordering": ("-history_date", "-history_id"),
                "verbose_name": "historical Invoice Item",
            },
        ),
        migrations.AlterModelOptions(
            name="invoice",
            options={"ordering": ["-updated_at"], "verbose_name": "Invoice"},
        ),
        migrations.AlterModelOptions(
            name="invoiceitem",
            options={"ordering": ["-updated_at"], "verbose_name": "Invoice Item"},
        ),
        migrations.AlterModelOptions(
            name="invoiceitemgroup",
            options={"ordering": ["-updated_at"], "verbose_name": "Invoice Group"},
        ),
        migrations.AlterModelOptions(
            name="invoiceitemtransaction",
            options={"ordering": ["-created_at"], "verbose_name": "Invoice Item Transaction"},
        ),
    ]