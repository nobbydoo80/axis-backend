# Generated by Django 3.1.6 on 2021-03-31 10:06

from django.db import migrations


def forward_data_migration(apps, schema):
    HIRLProject = apps.get_model("customer_hirl", "HIRLProject")
    for hirl_project in HIRLProject.objects.filter(home__isnull=False):
        hirl_project.h_number = 0
        home_status = hirl_project.home.homestatuses.filter(
            eep_program=hirl_project.eep_program
        ).first()

        hirl_project.home_status = home_status
        print(hirl_project.id)
        hirl_project.save()


def revert_migration(apps, schema):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("customer_hirl", "0137_auto_20210331_1000"),
    ]

    operations = [migrations.RunPython(code=forward_data_migration, reverse_code=revert_migration)]
