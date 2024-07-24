# Generated by Django 1.11.17 on 2019-05-22 00:25

from django.db import migrations, models
import django_fsm


class Migration(migrations.Migration):
    dependencies = [
        ("customer_hirl", "0004_auto_20190521_2311"),
    ]

    operations = [
        migrations.AddField(
            model_name="builderagreement",
            name="mailing_address_state",
            field=models.CharField(default="(empty)", max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="builderagreement",
            name="shipping_address_state",
            field=models.CharField(default="(empty)", max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="historicalbuilderagreement",
            name="mailing_address_state",
            field=models.CharField(default="(empty)", max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="historicalbuilderagreement",
            name="shipping_address_state",
            field=models.CharField(default="(empty)", max_length=100),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="builderagreement",
            name="state",
            field=django_fsm.FSMField(
                choices=[
                    ("new", "New"),
                    ("approved", "Approved"),
                    ("signed", "Signed"),
                    ("active", "Active"),
                    ("retired", "Retired"),
                ],
                default="new",
                max_length=50,
                protected=True,
            ),
        ),
        migrations.AlterField(
            model_name="historicalbuilderagreement",
            name="state",
            field=django_fsm.FSMField(
                choices=[
                    ("new", "New"),
                    ("approved", "Approved"),
                    ("signed", "Signed"),
                    ("active", "Active"),
                    ("retired", "Retired"),
                ],
                default="new",
                max_length=50,
                protected=True,
            ),
        ),
    ]