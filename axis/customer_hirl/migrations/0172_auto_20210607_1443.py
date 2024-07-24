# Generated by Django 3.1.9 on 2021-06-07 14:43

import axis.core.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("customer_hirl", "0171_auto_20210602_1813"),
    ]

    operations = [
        migrations.CreateModel(
            name="HIRLVerifierCommunityProject",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("hirl_id", models.PositiveIntegerField(verbose_name="Internal ID")),
                ("hirl_architect_id", models.PositiveIntegerField()),
                ("hirl_architect_contact_id", models.PositiveIntegerField()),
                ("hirl_developer_id", models.PositiveIntegerField()),
                ("hirl_developer_contact_id", models.PositiveIntegerField()),
                ("hirl_community_owner_id", models.PositiveIntegerField()),
                ("hirl_community_owner_contact_id", models.PositiveIntegerField()),
                ("data", axis.core.fields.AxisJSONField(default=dict)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AlterField(
            model_name="hirlproject",
            name="manual_billing_state",
            field=models.CharField(
                choices=[
                    ("", "Automatically"),
                    ("new", "New"),
                    ("new_queued", "New - Queued"),
                    ("new_notified", "New - Notified"),
                    ("notice_sent", "Notice Sent"),
                    ("completed", "Completed"),
                    ("complimentary", "Сomplimentary"),
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
            name="manual_billing_state",
            field=models.CharField(
                choices=[
                    ("", "Automatically"),
                    ("new", "New"),
                    ("new_queued", "New - Queued"),
                    ("new_notified", "New - Notified"),
                    ("notice_sent", "Notice Sent"),
                    ("completed", "Completed"),
                    ("complimentary", "Сomplimentary"),
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
    ]