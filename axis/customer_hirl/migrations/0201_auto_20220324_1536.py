# Generated by Django 3.2.12 on 2022-03-24 15:36

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("customer_hirl", "0200_alter_providedservice_options"),
    ]

    operations = [
        migrations.AddField(
            model_name="hirlproject",
            name="wri_certification_counter",
            field=models.IntegerField(
                default=0,
                help_text="Increased automatically when NGBS WRI or WaterSense Project have been certified",
                verbose_name="WRI Certification Counter",
            ),
        ),
        migrations.AddField(
            model_name="historicalhirlproject",
            name="wri_certification_counter",
            field=models.IntegerField(
                default=0,
                help_text="Increased automatically when NGBS WRI or WaterSense Project have been certified",
                verbose_name="WRI Certification Counter",
            ),
        ),
    ]
