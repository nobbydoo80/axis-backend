# Generated by Django 3.1.6 on 2021-03-04 19:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("home", "0017_auto_20210224_1038"),
        ("invoicing", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="HistoricalInvoiceItemGroup",
            fields=[
                (
                    "id",
                    models.IntegerField(
                        auto_created=True, blank=True, db_index=True, verbose_name="ID"
                    ),
                ),
                ("updated_at", models.DateTimeField(blank=True, editable=False)),
                ("created_at", models.DateTimeField(blank=True, editable=False)),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_date", models.DateTimeField()),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                (
                    "history_type",
                    models.CharField(
                        choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")], max_length=1
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        help_text="If None this means that Invoice Item Group has been created automatically",
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "history_user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "home_status",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="home.eepprogramhomestatus",
                    ),
                ),
                (
                    "invoice",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="invoicing.invoice",
                    ),
                ),
            ],
            options={
                "verbose_name": "historical Invoice Group",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": "history_date",
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="InvoiceItemGroup",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        help_text="If None this means that Invoice Item Group has been created automatically",
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="invoicing_invoice_item_groups",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "home_status",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="home.eepprogramhomestatus",
                    ),
                ),
                (
                    "invoice",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="invoicing.invoice",
                    ),
                ),
            ],
            options={
                "verbose_name": "Invoice Group",
            },
        ),
        migrations.RemoveField(
            model_name="invoicegroup",
            name="created_by",
        ),
        migrations.RemoveField(
            model_name="invoicegroup",
            name="home_status",
        ),
        migrations.RemoveField(
            model_name="invoicegroup",
            name="invoice",
        ),
        migrations.DeleteModel(
            name="HistoricalInvoiceGroup",
        ),
        migrations.AlterField(
            model_name="historicalinvoiceitem",
            name="group",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="invoicing.invoiceitemgroup",
            ),
        ),
        migrations.AlterField(
            model_name="invoiceitem",
            name="group",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="invoicing.invoiceitemgroup"
            ),
        ),
        migrations.DeleteModel(
            name="InvoiceGroup",
        ),
    ]
