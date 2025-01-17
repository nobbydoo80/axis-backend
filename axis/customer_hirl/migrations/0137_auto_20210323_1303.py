# Generated by Django 3.1.6 on 2021-03-23 13:03

from django.db import migrations


def forward_data_migration(apps, schema):
    HIRLRaterUser = apps.get_model("customer_hirl", "HIRLRaterUser")
    for rater in HIRLRaterUser.objects.all():
        try:
            rater.street_line1 = rater.data["AddressL1"]
            rater.street_line2 = rater.data["AddressL2"]
            rater.city = rater.data["City"]
            rater.state = rater.data["State"]
            rater.state_abbr = rater.data["HomeLocationState"]
            rater.zipcode = rater.data["Zip"]
            rater.email = rater.data["Email"]
        except KeyError:
            continue
        print(
            rater.street_line1,
            rater.street_line2,
            rater.city,
            rater.state,
            rater.state_abbr,
            rater.zipcode,
            rater.email,
        )
        rater.save()


def revert_migration(apps, schema):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("customer_hirl", "0136_auto_20210323_1301"),
    ]

    operations = [migrations.RunPython(code=forward_data_migration, reverse_code=revert_migration)]
