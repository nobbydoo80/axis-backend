# Generated by Django 1.11.17 on 2019-03-05 18:26

# NOTE: This migration exists because the ProgramBuilder code doesn't yet know how to detect
# updates to object pks, which the measure codes are.


from django.db import migrations


def forwards__structure_measure_names(apps, schema_editor):
    pass


def backwards__unstructure_measure_names(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("eep_program", "0006_program_submit"),
        ("django_input_collection", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(
            forwards__structure_measure_names, backwards__unstructure_measure_names
        ),
    ]
