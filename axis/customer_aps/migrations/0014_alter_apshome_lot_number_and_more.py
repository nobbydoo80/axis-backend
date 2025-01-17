# Generated by Django 4.0.8 on 2022-11-14 15:15

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("customer_aps", "0013_alter_historicalapshome_options_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="apshome",
            name="lot_number",
            field=models.CharField(
                blank=True,
                help_text='Enter the lot number of the project (typical for a "production builder" in a subdivision or development of multiple projects), or leave blank or "N/A" if unknown or not applicable.',
                max_length=30,
                null=True,
                verbose_name="Lot number",
            ),
        ),
        migrations.AlterField(
            model_name="historicalapshome",
            name="lot_number",
            field=models.CharField(
                blank=True,
                help_text='Enter the lot number of the project (typical for a "production builder" in a subdivision or development of multiple projects), or leave blank or "N/A" if unknown or not applicable.',
                max_length=30,
                null=True,
                verbose_name="Lot number",
            ),
        ),
    ]
