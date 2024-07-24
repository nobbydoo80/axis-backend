# Generated by Django 1.11.16 on 2018-10-10 23:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("django_input_collection", "0001_initial"),
        ("eep_program", "0003_historicaleepprogram_history_change_reason_foo"),
    ]

    operations = [
        migrations.AddField(
            model_name="eepprogram",
            name="collection_request",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="django_input_collection.CollectionRequest",
            ),
        ),
        migrations.AddField(
            model_name="historicaleepprogram",
            name="collection_request",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="django_input_collection.CollectionRequest",
            ),
        ),
    ]