# Generated by Django 3.1.6 on 2021-03-11 18:30

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("eep_program", "0019_auto_20210205_0946"),
    ]

    operations = [
        migrations.AddField(
            model_name="eepprogram",
            name="customer_hirl_certification_fee",
            field=models.DecimalField(
                decimal_places=2,
                default=0.0,
                help_text="Certification Fee that is adding to Invoice Item Group when CUSTOMER HIRL creates Project",
                max_digits=9,
            ),
        ),
        migrations.AddField(
            model_name="eepprogram",
            name="customer_hirl_per_unit_fee",
            field=models.DecimalField(
                decimal_places=2,
                default=0.0,
                help_text="Per Unit Fee that is adding to Invoice Item Group when CUSTOMER HIRL creates Project",
                max_digits=9,
            ),
        ),
        migrations.AddField(
            model_name="historicaleepprogram",
            name="customer_hirl_certification_fee",
            field=models.DecimalField(
                decimal_places=2,
                default=0.0,
                help_text="Certification Fee that is adding to Invoice Item Group when CUSTOMER HIRL creates Project",
                max_digits=9,
            ),
        ),
        migrations.AddField(
            model_name="historicaleepprogram",
            name="customer_hirl_per_unit_fee",
            field=models.DecimalField(
                decimal_places=2,
                default=0.0,
                help_text="Per Unit Fee that is adding to Invoice Item Group when CUSTOMER HIRL creates Project",
                max_digits=9,
            ),
        ),
    ]
