# Generated by Django 4.0.7 on 2022-09-14 22:38

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("filehandling", "0010_merge_20200701_0829"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="customerdocument",
            options={"ordering": ("-last_update",), "verbose_name": "Customer Document"},
        ),
        migrations.AlterModelOptions(
            name="historicalcustomerdocument",
            options={
                "get_latest_by": ("history_date", "history_id"),
                "ordering": ("-history_date", "-history_id"),
                "verbose_name": "historical Customer Document",
                "verbose_name_plural": "historical Customer Documents",
            },
        ),
        migrations.AlterField(
            model_name="asynchronousprocesseddocument",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="historicalcustomerdocument",
            name="history_date",
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name="historicalcustomerdocument",
            name="id",
            field=models.BigIntegerField(
                auto_created=True, blank=True, db_index=True, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="uploadfile",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
    ]