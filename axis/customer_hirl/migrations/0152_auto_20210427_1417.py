# Generated by Django 3.1.8 on 2021-04-27 14:17

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("customer_hirl", "0151_auto_20210422_1413"),
    ]

    operations = [
        migrations.AddField(
            model_name="hirlprojectregistration",
            name="is_using_sampling",
            field=models.BooleanField(
                null=True,
                verbose_name="Will the NGBS Sampling Protocol be utilized for this project",
            ),
        ),
        migrations.AddField(
            model_name="historicalhirlprojectregistration",
            name="is_using_sampling",
            field=models.BooleanField(
                null=True,
                verbose_name="Will the NGBS Sampling Protocol be utilized for this project",
            ),
        ),
        migrations.AlterField(
            model_name="hirlprojectregistration",
            name="application_packet_completion",
            field=models.CharField(
                blank=True,
                choices=[
                    ("architect", "Architect"),
                    ("builder", "Builder"),
                    ("community_owner", "Owner"),
                    ("developer", "Developer"),
                    ("verifier", "Verifier"),
                ],
                default="builder",
                max_length=255,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="hirlprojectregistration",
            name="entity_responsible_for_payment",
            field=models.CharField(
                blank=True,
                choices=[
                    ("architect", "Architect"),
                    ("builder", "Builder"),
                    ("community_owner", "Owner"),
                    ("developer", "Developer"),
                    ("verifier", "Verifier"),
                ],
                default="builder",
                max_length=255,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="hirlprojectregistration",
            name="multi_family_project_client",
            field=models.CharField(
                blank=True,
                choices=[
                    ("architect", "Architect"),
                    ("builder", "Builder"),
                    ("developer", "Developer"),
                    ("owner", "Owner"),
                ],
                max_length=100,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="hirlprojectregistration",
            name="party_named_on_certificate",
            field=models.CharField(
                blank=True,
                choices=[
                    ("architect", "Architect"),
                    ("builder", "Builder"),
                    ("community_owner", "Owner"),
                    ("developer", "Developer"),
                    ("verifier", "Verifier"),
                ],
                default="builder",
                max_length=255,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="historicalhirlprojectregistration",
            name="application_packet_completion",
            field=models.CharField(
                blank=True,
                choices=[
                    ("architect", "Architect"),
                    ("builder", "Builder"),
                    ("community_owner", "Owner"),
                    ("developer", "Developer"),
                    ("verifier", "Verifier"),
                ],
                default="builder",
                max_length=255,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="historicalhirlprojectregistration",
            name="entity_responsible_for_payment",
            field=models.CharField(
                blank=True,
                choices=[
                    ("architect", "Architect"),
                    ("builder", "Builder"),
                    ("community_owner", "Owner"),
                    ("developer", "Developer"),
                    ("verifier", "Verifier"),
                ],
                default="builder",
                max_length=255,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="historicalhirlprojectregistration",
            name="multi_family_project_client",
            field=models.CharField(
                blank=True,
                choices=[
                    ("architect", "Architect"),
                    ("builder", "Builder"),
                    ("developer", "Developer"),
                    ("owner", "Owner"),
                ],
                max_length=100,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="historicalhirlprojectregistration",
            name="party_named_on_certificate",
            field=models.CharField(
                blank=True,
                choices=[
                    ("architect", "Architect"),
                    ("builder", "Builder"),
                    ("community_owner", "Owner"),
                    ("developer", "Developer"),
                    ("verifier", "Verifier"),
                ],
                default="builder",
                max_length=255,
                null=True,
            ),
        ),
    ]
