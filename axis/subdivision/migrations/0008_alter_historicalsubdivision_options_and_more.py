# Generated by Django 4.0.6 on 2022-07-22 15:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("geographic", "0005_auto_20211021_1932"),
        ("subdivision", "0007_auto_20210719_1327"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="historicalsubdivision",
            options={
                "get_latest_by": ("history_date", "history_id"),
                "ordering": ("-history_date", "-history_id"),
                "verbose_name": "historical Subdivision",
                "verbose_name_plural": "historical Subdivisions",
            },
        ),
        migrations.AlterField(
            model_name="historicalsubdivision",
            name="history_date",
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name="subdivision",
            name="place",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="%(class)s_set",
                to="geographic.place",
            ),
        ),
    ]
