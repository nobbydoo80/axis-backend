# Generated by Django 3.1.6 on 2021-03-30 18:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("invoicing", "0005_auto_20210330_1801"),
    ]

    operations = [
        migrations.AddField(
            model_name="invoiceitemtransaction",
            name="created_by",
            field=models.ForeignKey(
                blank=True,
                help_text="If None this means that Invoice Transaction has been created automatically",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="invoicing_invoice_item_transactions",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="invoiceitemtransaction",
            name="note",
            field=models.TextField(blank=True),
        ),
    ]
