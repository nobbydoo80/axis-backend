"""mocked_responses.py - axis"""

__author__ = "Steven K"
__date__ = "1/10/23 08:32"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]


class MockReponse:
    """Fake Response"""

    def __init__(self, response_content, status_code=200):
        self.content = response_content
        self.status_code = status_code

    def json(self):
        return self.content


properties_valid = {
    "gbr_id": "OR10174306",
    "program_name": "State of Oregon Dept of Energy",
    "subdomain": "odoe-sandbox",
    "program": "odoe-sandbox",
    "formatted_address": "854 W 27th Ave, Eugene, OR, 97405",
    "address": {
        "address_line_1": "854 W 27TH AVE",
        "address_line_2": None,
        "city": "EUGENE",
        "state": "OR",
        "postal_code": "97405",
        "apn": None,
    },
    "latitude": 44.0287515,
    "longitude": -123.1060865,
    "exact_match": True,
    "building_type": "residential",
    "county": "LANE",
}

properties_invalid_address = {
    "error": "Bad Request",
    "description": "This request contains validation errors",
    "validation_errors": {
        "non_field_errors": [
            "AddressVerificationError: The address is invalid based on given inputs, or unrecognized by the validation service."
        ]
    },
    "override_token": None,
}

properties_invalid_program = {
    "error": "Bad Request",
    "description": "This request contains validation errors",
    "validation_errors": {
        "non_field_errors": [
            "80 Valley Vista Dr, Camarillo, CA, 93010 should be linked to Bay Area California (StopWaste) but you are not an active member of that Program. Please check your inputs or contact a Program admin: ealvarez@stopwaste.org"
        ]
    },
    "override_token": None,
}

assessment_with_no_pv_valid = {
    "status": None,
    "address": {
        "address_line_1": "854 W 27TH AVE",
        "address_line_2": None,
        "city": "EUGENE",
        "state": "OR",
        "postal_code": "97405",
        "latitude": "44.028752",
        "longitude": "-123.106087",
        "gbr_id": "OR10174306",
        "building_type": "residential",
        "county": "LANE",
    },
    "GreenBuildingVerificationType": "EPS",
    "GreenVerificationBody": "Energy Trust of Oregon",
    "GreenVerificationDate": "2023-01-18",
    "GreenVerificationMetric": 62,
    "GreenVerificationSource": "AXIS",
    "GreenVerificationStatus": "",
    "GreenVerificationURL": "https://None.pivotalenergy.net/api/v3/public_document/1Z/",
    "GreenBuildingVerificationKey": "000001",
    "GreenVerificationVersion": "",
    "GreenVerificationYear": 2023,
}

assessment_with_pv_valid = {
    "status": None,
    "address": {
        "address_line_1": "854 W 27TH AVE",
        "address_line_2": None,
        "city": "EUGENE",
        "state": "OR",
        "postal_code": "97405",
        "latitude": "44.028752",
        "longitude": "-123.106087",
        "gbr_id": "OR10174306",
        "building_type": "residential",
        "county": "LANE",
    },
    "GreenBuildingVerificationType": "EPS",
    "GreenVerificationBody": "Energy Trust of Oregon",
    "GreenVerificationDate": "2023-01-12",
    "GreenVerificationMetric": 62,
    "GreenVerificationSource": "AXIS",
    "GreenVerificationStatus": "",
    "GreenVerificationURL": "https://None.pivotalenergy.net/api/v3/public_document/1Z/",
    "GreenBuildingVerificationKey": "000001",
    "GreenVerificationVersion": "",
    "GreenVerificationYear": 2023,
    "PowerProductionType": "Photovoltaics",
    "PowerProductionYearInstall": 2023,
    "PowerProductionSize": "9601.0 kW DC",
    "PowerProductionAnnual": "1200 kWh/year",
    "PowerProductionAnnualStatus": "Estimated",
    "PowerProductionKeyNumeric": "000001",
}

assessment_invalid_data = {
    "error": "Bad Request",
    "description": "This request contains validation errors",
    "validation_errors": {
        "date": ["This field is required."],
        "report_url": ["This field is required."],
        "year_installed": ["This field is required."],
    },
    "override_token": None,
}

assessment_invalid_data_unavailable = {
    "error": "Service Unavailable",
    "description": "Address validity could not be determined at this time",
}

assessment_invalid_data_throttled = {
    "error": "Throttled",
    "description": "Request was throttled. Expected available in 1 second.",
}


def gbr_mocked_response(url, data=None, **_kw):
    if url.endswith("api/properties"):
        if "foo" in data["address_line_1"].lower():
            return MockReponse(properties_invalid_address, 400)
        if "CA" in data["state"]:
            return MockReponse(properties_invalid_program, 400)
        if "service" in data["address_line_1"].lower():
            return MockReponse(assessment_invalid_data_unavailable, 400)
        if "throttle" in data["address_line_1"].lower():
            return MockReponse(assessment_invalid_data_throttled, 400)
        return MockReponse(properties_valid, 201)
    if url.endswith("assessments/eps"):
        if data["date"] is None or data["report_url"] is None:
            return MockReponse(assessment_invalid_data, 400)

        if data["gbr_id"] == "SERVICE":
            return MockReponse(assessment_invalid_data_unavailable, 400)
        if data["gbr_id"] == "THROTTLE":
            return MockReponse(assessment_invalid_data_throttled, 400)

        # Update the response accordingly
        response = assessment_with_no_pv_valid
        if data["year_installed"]:  # PV
            response = assessment_with_pv_valid
        response["GreenVerificationMetric"] = data["score"]
        response["GreenVerificationDate"] = data["date"]
        return MockReponse(response, 201)
