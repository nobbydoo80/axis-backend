# Generated by Django 1.11.17 on 2019-01-22 22:36

from django.db import migrations


def copy_data(apps, schema_editor):
    CollectionInstrument = apps.get_model("django_input_collection", "CollectionInstrument")
    AxisSuggestedResponse = apps.get_model("checklist", "AxisSuggestedResponse")
    AxisBoundSuggestedResponse = apps.get_model("checklist", "AxisBoundSuggestedResponse")
    Through = CollectionInstrument.suggested_responses.through

    data_list = AxisSuggestedResponse.objects.values()
    to_insert = []
    for data in data_list:
        suggested_response_id = data.pop("suggestedresponse_ptr_id", None)
        data.pop("id")  # suggested_response.id is not the new bound id
        data.pop("data")  # The data is now available via the suggested_response fk

        instrument_ids = Through.objects.filter(
            suggestedresponse_id=suggested_response_id
        ).values_list("collectioninstrument_id", flat=True)
        for instrument_id in instrument_ids:
            data["collection_instrument_id"] = instrument_id

            if suggested_response_id:
                data["suggested_response_id"] = suggested_response_id

            to_insert.append(AxisBoundSuggestedResponse(**data))

    AxisBoundSuggestedResponse.objects.bulk_create(to_insert)


class Migration(migrations.Migration):
    dependencies = [
        ("checklist", "0008_axisboundsuggestedresponse"),
    ]

    operations = [migrations.RunPython(copy_data)]
