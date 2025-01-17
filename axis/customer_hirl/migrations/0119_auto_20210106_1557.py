# Generated by Django 3.1.3 on 2021-01-06 15:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("company", "0021_auto_20210104_1942"),
        ("customer_hirl", "0118_auto_20210106_1546"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="hirlproject",
            name="owner_company_name",
        ),
        migrations.RemoveField(
            model_name="hirlproject",
            name="owner_email",
        ),
        migrations.RemoveField(
            model_name="hirlproject",
            name="owner_first_name",
        ),
        migrations.RemoveField(
            model_name="hirlproject",
            name="owner_last_name",
        ),
        migrations.RemoveField(
            model_name="hirlproject",
            name="owner_phone",
        ),
        migrations.RemoveField(
            model_name="historicalhirlproject",
            name="owner_company_name",
        ),
        migrations.RemoveField(
            model_name="historicalhirlproject",
            name="owner_email",
        ),
        migrations.RemoveField(
            model_name="historicalhirlproject",
            name="owner_first_name",
        ),
        migrations.RemoveField(
            model_name="historicalhirlproject",
            name="owner_last_name",
        ),
        migrations.RemoveField(
            model_name="historicalhirlproject",
            name="owner_phone",
        ),
        migrations.AddField(
            model_name="hirlproject",
            name="community_owner_organization",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="company.communityownerorganization",
            ),
        ),
        migrations.AddField(
            model_name="historicalhirlproject",
            name="community_owner_organization",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="company.communityownerorganization",
            ),
        ),
    ]
