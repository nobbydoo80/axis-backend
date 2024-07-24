# Generated by Django 3.1.8 on 2021-05-07 13:34

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("customer_hirl", "0156_auto_20210428_0831"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="hirlprojectregistration",
            name="is_using_sampling",
        ),
        migrations.RemoveField(
            model_name="historicalhirlprojectregistration",
            name="is_using_sampling",
        ),
        migrations.AddField(
            model_name="hirlprojectregistration",
            name="sampling",
            field=models.CharField(
                choices=[
                    ("no_sampling", "No Sampling"),
                    ("testing_and_practices_only", "For Energy efficiency testing practices only"),
                    ("all", "For All or most NGBS practices"),
                ],
                max_length=30,
                null=True,
                verbose_name="Do you intend to employ the NGBS Green Alternative Multifamily Verification Protocol (Sampling) ?",
            ),
        ),
        migrations.AddField(
            model_name="historicalhirlprojectregistration",
            name="sampling",
            field=models.CharField(
                choices=[
                    ("no_sampling", "No Sampling"),
                    ("testing_and_practices_only", "For Energy efficiency testing practices only"),
                    ("all", "For All or most NGBS practices"),
                ],
                max_length=30,
                null=True,
                verbose_name="Do you intend to employ the NGBS Green Alternative Multifamily Verification Protocol (Sampling) ?",
            ),
        ),
    ]