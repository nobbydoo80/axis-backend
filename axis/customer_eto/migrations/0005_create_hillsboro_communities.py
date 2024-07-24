# Generated by Django 1.11.17 on 2019-06-12 20:22

from django.db import migrations


def forward(apps, schema_editor):
    ContentType = apps.get_model("contenttypes.ContentType")
    Relationship = apps.get_model("relationship.Relationship")
    City = apps.get_model("geographic.City")
    Company = apps.get_model("company.Company")
    Community = apps.get_model("community.Community")

    community_ct = ContentType.objects.get_for_model(Community)
    hillsboro_city = City.objects.get(
        name="Hillsboro", county__name="Washington", county__state="OR"
    )

    customer = Company.objects.get(slug="eto")
    kwargs = {
        "city": hillsboro_city,
        "county": hillsboro_city.county,
    }

    if not Community.objects.filter(
        name="Reed's Crossing", slug="reeds-crossing", **kwargs
    ).exists():
        community = Community(name="Reed's Crossing", slug="reeds-crossing", **kwargs)
        Community.objects.bulk_create([community])
    community = Community.objects.get(name="Reed's Crossing", slug="reeds-crossing", **kwargs)
    Relationship.objects.get_or_create(
        content_type=community_ct,
        object_id=community.id,
        company=customer,
        is_attached=True,
        is_viewable=True,
        is_owned=True,
    )

    if not Community.objects.filter(
        name="Rosedale Parks", slug="rosedale-parks", **kwargs
    ).exists():
        community = Community(name="Rosedale Parks", slug="rosedale-parks", **kwargs)
        Community.objects.bulk_create([community])
    community = Community.objects.get(name="Rosedale Parks", slug="rosedale-parks", **kwargs)
    Relationship.objects.get_or_create(
        content_type=community_ct,
        object_id=community.id,
        company=customer,
        is_attached=True,
        is_viewable=True,
        is_owned=True,
    )


def backward(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("contenttypes", "__first__"),
        ("relationship", "0002_historicalrelationship_history_change_reason_foo"),
        ("geographic", "0002_auto_20190531_1224"),
        ("company", "0003_auto_20181010_2316"),
        ("community", "0003_historicalcommunity_history_change_reason_foo"),
        ("customer_eto", "0004_payment_modifications"),
    ]

    operations = [migrations.RunPython(forward, backward)]
