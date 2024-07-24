# Generated by Django 3.1.6 on 2021-03-18 17:46

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("customer_hirl", "0134_auto_20210318_1728"),
    ]

    operations = [
        migrations.AlterField(
            model_name="hirlproject",
            name="application_packet_completion",
            field=models.CharField(
                blank=True,
                choices=[
                    ("builder", "Builder"),
                    ("architect", "Architect"),
                    ("community_owner", "Owner"),
                    ("developer", "Developer"),
                ],
                default="builder",
                max_length=255,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="hirlproject",
            name="party_named_on_certificate",
            field=models.CharField(
                blank=True,
                choices=[
                    ("builder", "Builder"),
                    ("architect", "Architect"),
                    ("community_owner", "Owner"),
                    ("developer", "Developer"),
                ],
                default="builder",
                max_length=255,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="historicalhirlproject",
            name="application_packet_completion",
            field=models.CharField(
                blank=True,
                choices=[
                    ("builder", "Builder"),
                    ("architect", "Architect"),
                    ("community_owner", "Owner"),
                    ("developer", "Developer"),
                ],
                default="builder",
                max_length=255,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="historicalhirlproject",
            name="party_named_on_certificate",
            field=models.CharField(
                blank=True,
                choices=[
                    ("builder", "Builder"),
                    ("architect", "Architect"),
                    ("community_owner", "Owner"),
                    ("developer", "Developer"),
                ],
                default="builder",
                max_length=255,
                null=True,
            ),
        ),
        migrations.DeleteModel(
            name="HIRLResponsibleName",
        ),
    ]