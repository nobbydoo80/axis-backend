# Generated by Django 4.1.5 on 2023-02-14 09:18

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("customer_hirl", "0227_alter_hirlproject_lot_number_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="hirlprojectregistration",
            options={
                "ordering": ("-id",),
                "verbose_name": "Project Registration",
                "verbose_name_plural": "Project Registrations",
            },
        ),
        migrations.AddField(
            model_name="hirlproject",
            name="accessory_dwelling_unit_description",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="hirlproject",
            name="is_accessory_dwelling_unit",
            field=models.BooleanField(
                default=False,
                verbose_name="Is this property associated with an Accessory Dwelling Unit (ADU) seeking certification?",
            ),
        ),
        migrations.AddField(
            model_name="historicalhirlproject",
            name="accessory_dwelling_unit_description",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="historicalhirlproject",
            name="is_accessory_dwelling_unit",
            field=models.BooleanField(
                default=False,
                verbose_name="Is this property associated with an Accessory Dwelling Unit (ADU) seeking certification?",
            ),
        ),
    ]