# Generated by Django 3.2.12 on 2022-03-22 20:30

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("customer_hirl", "0198_auto_20220118_1909"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="providedservice",
            options={"ordering": ("order",)},
        ),
        migrations.AddField(
            model_name="providedservice",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="providedservice",
            name="last_update",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name="providedservice",
            name="order",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="providedservice",
            name="slug",
            field=models.SlugField(default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="hirlproject",
            name="billing_state",
            field=models.CharField(
                blank=True,
                choices=[
                    ("", "Automatically"),
                    ("new", "New"),
                    ("new_queued", "New - Queued"),
                    ("new_notified", "New - Notified"),
                    ("notice_sent", "Notice Sent"),
                    ("completed", "Completed"),
                    ("complimentary", "Complimentary"),
                    ("not_pursuing", "Not pursuing"),
                    ("test", "Test"),
                    ("void", "Void"),
                    ("4300", "4300"),
                ],
                default="new",
                max_length=30,
                verbose_name="Billing State",
            ),
        ),
        migrations.AlterField(
            model_name="hirlproject",
            name="manual_billing_state",
            field=models.CharField(
                blank=True,
                choices=[
                    ("", "Automatically"),
                    ("new", "New"),
                    ("new_queued", "New - Queued"),
                    ("new_notified", "New - Notified"),
                    ("notice_sent", "Notice Sent"),
                    ("completed", "Completed"),
                    ("complimentary", "Complimentary"),
                    ("not_pursuing", "Not pursuing"),
                    ("test", "Test"),
                    ("void", "Void"),
                    ("4300", "4300"),
                ],
                default="",
                help_text="Manual override Billing State",
                max_length=30,
                verbose_name="Billing State Override",
            ),
        ),
        migrations.AlterField(
            model_name="historicalhirlproject",
            name="billing_state",
            field=models.CharField(
                blank=True,
                choices=[
                    ("", "Automatically"),
                    ("new", "New"),
                    ("new_queued", "New - Queued"),
                    ("new_notified", "New - Notified"),
                    ("notice_sent", "Notice Sent"),
                    ("completed", "Completed"),
                    ("complimentary", "Complimentary"),
                    ("not_pursuing", "Not pursuing"),
                    ("test", "Test"),
                    ("void", "Void"),
                    ("4300", "4300"),
                ],
                default="new",
                max_length=30,
                verbose_name="Billing State",
            ),
        ),
        migrations.AlterField(
            model_name="historicalhirlproject",
            name="manual_billing_state",
            field=models.CharField(
                blank=True,
                choices=[
                    ("", "Automatically"),
                    ("new", "New"),
                    ("new_queued", "New - Queued"),
                    ("new_notified", "New - Notified"),
                    ("notice_sent", "Notice Sent"),
                    ("completed", "Completed"),
                    ("complimentary", "Complimentary"),
                    ("not_pursuing", "Not pursuing"),
                    ("test", "Test"),
                    ("void", "Void"),
                    ("4300", "4300"),
                ],
                default="",
                help_text="Manual override Billing State",
                max_length=30,
                verbose_name="Billing State Override",
            ),
        ),
        migrations.AlterField(
            model_name="providedservice",
            name="name",
            field=models.CharField(max_length=255),
        ),
    ]
