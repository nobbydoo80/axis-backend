# Generated by Django 4.0.7 on 2022-10-10 16:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0024_alter_eepprogramhomestatus_home_and_more"),
        ("scheduling", "0014_alter_constructionstage_id_alter_task_id_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="historicaltask",
            name="home",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="home.home",
            ),
        ),
        migrations.AddField(
            model_name="task",
            name="home",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="home.home"
            ),
        ),
    ]