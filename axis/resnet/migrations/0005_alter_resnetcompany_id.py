# Generated by Django 4.0.7 on 2022-09-14 17:23

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("resnet", "0004_alter_resnetcompany_id_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="resnetcompany",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
    ]
