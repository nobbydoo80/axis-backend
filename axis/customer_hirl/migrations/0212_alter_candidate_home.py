# Generated by Django 4.0.7 on 2022-09-14 23:43

from django.conf import settings

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0024_alter_eepprogramhomestatus_home_and_more"),
        ("customer_hirl", "0211_builderagreement_initiator_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="candidate",
            name="home",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="home.home"),
        ),
    ]