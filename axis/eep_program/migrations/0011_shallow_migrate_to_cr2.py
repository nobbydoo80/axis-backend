# Generated by Django 1.11.17 on 2019-04-15 13:31

from django.db import migrations


def set_collection_from_program(home_status):
    # homestatus.set_collection_from_program()

    from django_input_collection.models.utils import clone_collection_request

    collection_request = home_status.eep_program.collection_request
    cloned = clone_collection_request(collection_request)
    home_status.collection_request = cloned
    home_status.save()


# pylint: disable=invalid-name
def forward(apps, schema_editor):
    EEPProgram = apps.get_model("eep_program", "EEPProgram")

    from ..program_builder.energy_star_3_08 import EnergyStar3Rev08

    convert = {
        "energy-star-version-3-rev-08": EnergyStar3Rev08,
    }

    num_programs = len(convert)
    for i, (slug, ProgramBuilderClass) in enumerate(convert.items()):
        program = EEPProgram.objects.get(slug=slug)
        home_statuses = program.homestatuses.filter(collection_request=None).select_related(
            "eep_program"
        )
        total = home_statuses.count()
        print(total, slug, ProgramBuilderClass)

        builder = ProgramBuilderClass()
        builder.build("rater")
        for j, home_status in enumerate(home_statuses):
            set_collection_from_program(home_status)


def backward(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("eep_program", "0010_remove_measure_migration"),
    ]

    operations = []
