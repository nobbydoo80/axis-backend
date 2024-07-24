# Generated by Django 3.1.6 on 2021-03-18 17:28

from django.db import migrations, models
import phonenumber_field.modelfields


class Migration(migrations.Migration):
    dependencies = [
        ("customer_hirl", "0133_auto_20210315_1207"),
    ]

    operations = [
        migrations.AlterField(
            model_name="hirlproject",
            name="architect_phone",
            field=phonenumber_field.modelfields.PhoneNumberField(
                blank=True, max_length=128, null=True, region=None
            ),
        ),
        migrations.AlterField(
            model_name="hirlproject",
            name="billing_phone",
            field=phonenumber_field.modelfields.PhoneNumberField(
                blank=True, max_length=128, null=True, region=None
            ),
        ),
        migrations.AlterField(
            model_name="hirlproject",
            name="builder_phone_number",
            field=phonenumber_field.modelfields.PhoneNumberField(
                blank=True, max_length=128, null=True, region=None
            ),
        ),
        migrations.AlterField(
            model_name="hirlproject",
            name="developer_phone",
            field=phonenumber_field.modelfields.PhoneNumberField(
                blank=True, max_length=128, null=True, region=None
            ),
        ),
        migrations.AlterField(
            model_name="hirlproject",
            name="entity_responsible_for_payment",
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
            name="marketing_phone",
            field=phonenumber_field.modelfields.PhoneNumberField(
                blank=True, max_length=128, null=True, region=None
            ),
        ),
        migrations.AlterField(
            model_name="hirlproject",
            name="owner_phone",
            field=phonenumber_field.modelfields.PhoneNumberField(
                blank=True, max_length=128, null=True, region=None
            ),
        ),
        migrations.AlterField(
            model_name="hirlproject",
            name="project_contact_phone_number",
            field=phonenumber_field.modelfields.PhoneNumberField(
                blank=True, max_length=128, null=True, region=None
            ),
        ),
        migrations.AlterField(
            model_name="hirlproject",
            name="sales_phone",
            field=phonenumber_field.modelfields.PhoneNumberField(
                blank=True, max_length=128, null=True, region=None
            ),
        ),
        migrations.AlterField(
            model_name="historicalhirlproject",
            name="architect_phone",
            field=phonenumber_field.modelfields.PhoneNumberField(
                blank=True, max_length=128, null=True, region=None
            ),
        ),
        migrations.AlterField(
            model_name="historicalhirlproject",
            name="billing_phone",
            field=phonenumber_field.modelfields.PhoneNumberField(
                blank=True, max_length=128, null=True, region=None
            ),
        ),
        migrations.AlterField(
            model_name="historicalhirlproject",
            name="builder_phone_number",
            field=phonenumber_field.modelfields.PhoneNumberField(
                blank=True, max_length=128, null=True, region=None
            ),
        ),
        migrations.AlterField(
            model_name="historicalhirlproject",
            name="developer_phone",
            field=phonenumber_field.modelfields.PhoneNumberField(
                blank=True, max_length=128, null=True, region=None
            ),
        ),
        migrations.AlterField(
            model_name="historicalhirlproject",
            name="entity_responsible_for_payment",
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
            name="marketing_phone",
            field=phonenumber_field.modelfields.PhoneNumberField(
                blank=True, max_length=128, null=True, region=None
            ),
        ),
        migrations.AlterField(
            model_name="historicalhirlproject",
            name="owner_phone",
            field=phonenumber_field.modelfields.PhoneNumberField(
                blank=True, max_length=128, null=True, region=None
            ),
        ),
        migrations.AlterField(
            model_name="historicalhirlproject",
            name="project_contact_phone_number",
            field=phonenumber_field.modelfields.PhoneNumberField(
                blank=True, max_length=128, null=True, region=None
            ),
        ),
        migrations.AlterField(
            model_name="historicalhirlproject",
            name="sales_phone",
            field=phonenumber_field.modelfields.PhoneNumberField(
                blank=True, max_length=128, null=True, region=None
            ),
        ),
    ]
