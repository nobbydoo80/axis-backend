# Generated by Django 4.0.7 on 2022-09-14 21:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0023_alter_eepprogramhomestatus_home_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="eepprogramhomestatus",
            name="home",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="homestatuses",
                to="home.home",
            ),
        ),
        migrations.AlterField(
            model_name="eepprogramhomestatus",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
    ]