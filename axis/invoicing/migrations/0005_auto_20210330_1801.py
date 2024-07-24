# Generated by Django 3.1.6 on 2021-03-30 18:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("invoicing", "0004_auto_20210316_1934"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="historicalinvoice",
            name="paid_at",
        ),
        migrations.RemoveField(
            model_name="historicalinvoice",
            name="total_paid",
        ),
        migrations.RemoveField(
            model_name="invoice",
            name="paid_at",
        ),
        migrations.RemoveField(
            model_name="invoice",
            name="total_paid",
        ),
        migrations.CreateModel(
            name="InvoiceItemTransaction",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("amount", models.DecimalField(decimal_places=2, default=0.0, max_digits=9)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "item",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="transactions",
                        to="invoicing.invoiceitem",
                    ),
                ),
            ],
        ),
    ]
