# Generated by Django 4.0.7 on 2022-09-14 19:34

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("incentive_payment", "0003_alter_historicalincentivedistribution_options_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="incentivedistribution",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="incentivepaymentstatus",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
    ]
