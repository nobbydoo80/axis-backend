# Generated by Django 4.0.8 on 2023-01-23 15:40

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("scheduling", "0019_remove_historicaltask_date_remove_task_date_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="tasktype",
            options={"ordering": ("-priority", "name")},
        ),
        migrations.AddField(
            model_name="historicaltasktype",
            name="priority",
            field=models.IntegerField(default=0, help_text="Using for ordering items in list"),
        ),
        migrations.AddField(
            model_name="tasktype",
            name="priority",
            field=models.IntegerField(default=0, help_text="Using for ordering items in list"),
        ),
    ]
