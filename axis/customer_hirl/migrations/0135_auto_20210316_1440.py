# Generated by Django 3.1.6 on 2021-03-16 14:40

from django.db import migrations


def forward_data_migration(apps, schema):
    HIRLRaterUser = apps.get_model("customer_hirl", "HIRLRaterUser")
    for rater in HIRLRaterUser.objects.all():
        rater.assigned_verifier_id = rater.data["AssignedVerifierID"]
        print(rater.assigned_verifier_id)
        rater.save()


def revert_migration(apps, schema):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("customer_hirl", "0134_hirlrateruser_assigned_verifier_id"),
    ]

    operations = [migrations.RunPython(code=forward_data_migration, reverse_code=revert_migration)]