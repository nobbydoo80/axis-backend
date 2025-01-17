# Generated by Django 4.0.7 on 2022-09-14 17:17

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("reso", "0007_merge_20200701_0829"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="historicalresogreenverification",
            options={
                "get_latest_by": ("history_date", "history_id"),
                "ordering": ("-history_date", "-history_id"),
                "verbose_name": "historical reso green verification",
                "verbose_name_plural": "historical reso green verifications",
            },
        ),
        migrations.AlterModelOptions(
            name="historicalresohome",
            options={
                "get_latest_by": ("history_date", "history_id"),
                "ordering": ("-history_date", "-history_id"),
                "verbose_name": "historical reso home",
                "verbose_name_plural": "historical reso homes",
            },
        ),
        migrations.AlterField(
            model_name="historicalresogreenverification",
            name="history_date",
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name="historicalresogreenverification",
            name="id",
            field=models.BigIntegerField(
                auto_created=True, blank=True, db_index=True, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="historicalresohome",
            name="history_date",
            field=models.DateTimeField(db_index=True),
        ),
    ]
