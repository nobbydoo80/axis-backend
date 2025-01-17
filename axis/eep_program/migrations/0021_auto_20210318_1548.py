# Generated by Django 3.1.6 on 2021-03-18 15:48

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("eep_program", "0020_auto_20210311_1830"),
    ]

    operations = [
        migrations.AlterField(
            model_name="eepprogram",
            name="customer_hirl_certification_fee",
            field=models.DecimalField(
                decimal_places=2,
                default=0.0,
                help_text="Certification Fee that is adding to Invoice Item Group when CUSTOMER HIRL creating Project. ATTENTION: This is a base value that affects on ALL certification fees for this program. Fees calculation performs in method `calculate_certification_fees_cost()`",
                max_digits=9,
                verbose_name="Base Certification Fee",
            ),
        ),
        migrations.AlterField(
            model_name="eepprogram",
            name="customer_hirl_per_unit_fee",
            field=models.DecimalField(
                decimal_places=2,
                default=0.0,
                help_text="Per Unit Fee that is adding to Invoice Item Group when CUSTOMER HIRL creating Project. ATTENTION: This is a base value that affects on ALL unit fees for this program.",
                max_digits=9,
                verbose_name="Base Per Unit Fee",
            ),
        ),
        migrations.AlterField(
            model_name="historicaleepprogram",
            name="customer_hirl_certification_fee",
            field=models.DecimalField(
                decimal_places=2,
                default=0.0,
                help_text="Certification Fee that is adding to Invoice Item Group when CUSTOMER HIRL creating Project. ATTENTION: This is a base value that affects on ALL certification fees for this program. Fees calculation performs in method `calculate_certification_fees_cost()`",
                max_digits=9,
                verbose_name="Base Certification Fee",
            ),
        ),
        migrations.AlterField(
            model_name="historicaleepprogram",
            name="customer_hirl_per_unit_fee",
            field=models.DecimalField(
                decimal_places=2,
                default=0.0,
                help_text="Per Unit Fee that is adding to Invoice Item Group when CUSTOMER HIRL creating Project. ATTENTION: This is a base value that affects on ALL unit fees for this program.",
                max_digits=9,
                verbose_name="Base Per Unit Fee",
            ),
        ),
    ]
