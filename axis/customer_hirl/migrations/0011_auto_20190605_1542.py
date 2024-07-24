# Generated by Django 1.11.17 on 2019-06-05 15:42

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("customer_hirl", "0010_auto_20190604_0010"),
    ]

    operations = [
        migrations.AlterField(
            model_name="builderagreement",
            name="use_payment_contact_in_ngbs_green_projects",
            field=models.BooleanField(
                default=False,
                verbose_name="Should this person be contact for payment on future NGBS Green Projects?",
            ),
        ),
        migrations.AlterField(
            model_name="historicalbuilderagreement",
            name="use_payment_contact_in_ngbs_green_projects",
            field=models.BooleanField(
                default=False,
                verbose_name="Should this person be contact for payment on future NGBS Green Projects?",
            ),
        ),
    ]
