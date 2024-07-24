# Generated by Django 1.11.26 on 2020-07-13 20:26

import phonenumber_field.modelfields
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("company", "0012_auto_20200605_1822"),
    ]

    operations = [
        migrations.AlterField(
            model_name="company",
            name="office_phone",
            field=phonenumber_field.modelfields.PhoneNumberField(
                help_text="Enter the main company phone number in the format XXX-XXX-XXXX.",
                max_length=128,
                null=True,
                region=None,
            ),
        ),
        migrations.AlterField(
            model_name="contact",
            name="phone",
            field=phonenumber_field.modelfields.PhoneNumberField(
                help_text="Enter the main company phone number in the format XXX-XXX-XXXX.",
                max_length=128,
                null=True,
                region=None,
            ),
        ),
        migrations.AlterField(
            model_name="historicalbuilderorganization",
            name="office_phone",
            field=phonenumber_field.modelfields.PhoneNumberField(
                help_text="Enter the main company phone number in the format XXX-XXX-XXXX.",
                max_length=128,
                null=True,
                region=None,
            ),
        ),
        migrations.AlterField(
            model_name="historicalcompany",
            name="office_phone",
            field=phonenumber_field.modelfields.PhoneNumberField(
                help_text="Enter the main company phone number in the format XXX-XXX-XXXX.",
                max_length=128,
                null=True,
                region=None,
            ),
        ),
        migrations.AlterField(
            model_name="historicaleeporganization",
            name="office_phone",
            field=phonenumber_field.modelfields.PhoneNumberField(
                help_text="Enter the main company phone number in the format XXX-XXX-XXXX.",
                max_length=128,
                null=True,
                region=None,
            ),
        ),
        migrations.AlterField(
            model_name="historicalgeneralorganization",
            name="office_phone",
            field=phonenumber_field.modelfields.PhoneNumberField(
                help_text="Enter the main company phone number in the format XXX-XXX-XXXX.",
                max_length=128,
                null=True,
                region=None,
            ),
        ),
        migrations.AlterField(
            model_name="historicalhvacorganization",
            name="office_phone",
            field=phonenumber_field.modelfields.PhoneNumberField(
                help_text="Enter the main company phone number in the format XXX-XXX-XXXX.",
                max_length=128,
                null=True,
                region=None,
            ),
        ),
        migrations.AlterField(
            model_name="historicalproviderorganization",
            name="office_phone",
            field=phonenumber_field.modelfields.PhoneNumberField(
                help_text="Enter the main company phone number in the format XXX-XXX-XXXX.",
                max_length=128,
                null=True,
                region=None,
            ),
        ),
        migrations.AlterField(
            model_name="historicalqaorganization",
            name="office_phone",
            field=phonenumber_field.modelfields.PhoneNumberField(
                help_text="Enter the main company phone number in the format XXX-XXX-XXXX.",
                max_length=128,
                null=True,
                region=None,
            ),
        ),
        migrations.AlterField(
            model_name="historicalraterorganization",
            name="office_phone",
            field=phonenumber_field.modelfields.PhoneNumberField(
                help_text="Enter the main company phone number in the format XXX-XXX-XXXX.",
                max_length=128,
                null=True,
                region=None,
            ),
        ),
        migrations.AlterField(
            model_name="historicalutilityorganization",
            name="office_phone",
            field=phonenumber_field.modelfields.PhoneNumberField(
                help_text="Enter the main company phone number in the format XXX-XXX-XXXX.",
                max_length=128,
                null=True,
                region=None,
            ),
        ),
    ]
