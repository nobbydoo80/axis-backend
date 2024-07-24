"""utils.py: Django floorplan"""


import logging

from . import messages

__author__ = "Steven Klass"
__date__ = "10/28/15 11:43 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


def clear_approval_and_request_new(
    floorplan, homestatus, approval_entity, user, changed_fields=None
):
    """This will send a message and reset the reviewed field for APS"""

    previous_approval = floorplan.revoke_approval(homestatus=homestatus, user=user)

    # Clear approval if it was previously given
    if previous_approval:
        message = messages.FloorplanRemrateDataChangeMessage()
    else:
        message = messages.FloorplanRemrateDataAddMessage()

    verbose_names = {
        "remrate_data_file": "REM/Rate® BLG File",
        "remrate_target": "REM/Rate® Data",
    }
    if changed_fields is None:
        changed_fields = []
    context = {
        "company": user.company,
        "floorplan": "{}".format(floorplan),
        "url": floorplan.get_absolute_url(),
        "data": " and ".join([verbose_names[name] for name in changed_fields]),
    }
    message(url=floorplan.get_absolute_url()).send(context=context, company=approval_entity)
    return True


def serialize_floorplan_input_rem_rate(obj):
    """Simulation serialized to common names we can use regardless of input source."""
    data = obj
    # data = {
    #     'id': obj.axis_id,
    #     'summary': {
    #         'builder_name': obj.building.project.builder_name,
    #         'building_name': obj.building.project.name,
    #         'date': obj.building.project.rating_date,
    #         'property': {
    #             'address': obj.building.project.property_address,
    #             'city': obj.building.project.property_city,
    #             'city': obj.building.project.property_state,
    #         },
    #         'rater': {
    #             'org': obj.building.project.rating_organization,
    #             'name': obj.building.project.rater_name,
    #             'id': obj.building.project.rater_id,
    #         },
    #         'meta': {
    #             'resnet_id': obj.building.project.resnet_registry_id,
    #             'number': obj.building.project.rating_number,
    #             'export_type': obj.get_export_type_display(),
    #         },
    #     },
    #
    # }
    return data


def serialize_floorplan_input_ekotrope(obj):
    """Project serialized to common names we can use regardless of input source."""
    project = obj.project
    houseplan = obj
    analysis = obj.project.analysis_set.filter(id=houseplan.id).first()
    data = {
        "project": project.data,
        "houseplan": houseplan.data if houseplan else None,
        "analysis": analysis.data if analysis else None,
    }

    compliance_serialized_names = {
        True: "Passes",
        "warn": "Warn",
        False: "Fails",
        None: "-",
    }

    if analysis:
        data["analysis"]["compliances"] = {
            k: compliance_serialized_names[v] for k, v in analysis.compliances.items()
        }
    # data = {
    #     'id': obj['id'],
    #     'summary': {
    #         'builder_name': obj['builder'],
    #         'building_name': obj['community'],
    #         'date': None,
    #         'property': {
    #             'address': obj['location']['streetAddress'],
    #             'city': obj['location']['city'],
    #             'state': obj['location']['state'],
    #         },
    #         'rater': {
    #             'org': obj['hersRatingDetails']['rater']['ratingCompany']['name'],
    #             'name': obj['hersRatingDetails']['rater']['name'],
    #             'id': None,
    #         },
    #         'meta': {},
    #     },
    #
    # }
    return data
