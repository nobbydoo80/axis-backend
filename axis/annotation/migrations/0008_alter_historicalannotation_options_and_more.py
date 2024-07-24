# Generated by Django 4.0.7 on 2022-09-12 19:31

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("annotation", "0007_auto_20200812_1309"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="historicalannotation",
            options={
                "get_latest_by": ("history_date", "history_id"),
                "ordering": ("-history_date", "-history_id"),
                "verbose_name": "historical annotation",
                "verbose_name_plural": "historical annotations",
            },
        ),
        migrations.AlterField(
            model_name="annotation",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="historicalannotation",
            name="history_date",
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name="historicalannotation",
            name="id",
            field=models.BigIntegerField(
                auto_created=True, blank=True, db_index=True, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="type",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
    ]
