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

    from ..program_builder.doe_zero_energy_06_performance import DOEZeroEnergy05Performance
    from ..program_builder.earth_advantage import EarthAdvantageCertifiedHome
    from ..program_builder.energy_star_31_08 import EnergyStar31Rev08
    from ..program_builder.energy_star_32_08 import EnergyStar32Rev08
    from ..program_builder.indoor_airplus_01_03 import IndoorAirPLUS_01_03
    from ..program_builder.ngbs_sf_new_construction_2012 import NGBSSFNewConstruction2012
    from ..program_builder.eto_legacy import Eto2018, Eto2017, Eto2016, Eto2015, Eto2014

    convert = {
        "doe-zero-energy-ready-rev-05-performance-path": DOEZeroEnergy05Performance,
        "earth-advantage-certified-home": EarthAdvantageCertifiedHome,
        "energy-star-version-31-rev-08": EnergyStar31Rev08,
        "energy-star-version-32-rev-08": EnergyStar32Rev08,
        "indoor-airplus-version-1-rev-03": IndoorAirPLUS_01_03,
        "ngbs-sf-new-construction-2012": NGBSSFNewConstruction2012,
        "eto-2018": Eto2018,
        "eto-2017": Eto2017,
        "eto-2016": Eto2016,
        "eto-2015": Eto2015,
        "eto": Eto2014,
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
        ("eep_program", "0007_auto_20190305_1826"),
    ]

    operations = []
