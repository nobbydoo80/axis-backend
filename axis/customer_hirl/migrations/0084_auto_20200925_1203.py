# Generated by Django 2.2 on 2020-09-25 12:03

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("customer_hirl", "0083_hirlrateruser_hirl_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="hirlbuilderorganization",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="hirlbuilderorganization",
            name="hirl_id",
            field=models.PositiveIntegerField(default=0, verbose_name="Internal ID"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="hirlbuilderorganization",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name="hirlraterorganization",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="hirlraterorganization",
            name="hirl_id",
            field=models.PositiveIntegerField(default=0, verbose_name="Internal ID"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="hirlraterorganization",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name="hirlrateruser",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="hirlrateruser",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
    ]
