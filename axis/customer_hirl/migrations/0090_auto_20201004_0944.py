# Generated by Django 2.2 on 2020-10-04 09:44

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("customer_hirl", "0089_auto_20201002_1720"),
    ]

    operations = [
        migrations.AddField(
            model_name="hirlbuilderagreementstatus",
            name="hirl_verifier_id",
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="hirlverifieragreementstatus",
            name="hirl_builder_id",
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
    ]
