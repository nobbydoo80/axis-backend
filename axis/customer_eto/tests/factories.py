"""factories.py: Django incentive_payment"""

import logging
import random
from urllib.error import HTTPError

import xmltodict

from django.contrib.auth import get_user_model

from axis.home.tests.factories import certified_home_with_basic_eep_factory
from axis.incentive_payment.tests.factories import (
    basic_pending_builder_incentive_distribution_factory,
)
from ..models import FastTrackSubmission

__author__ = "Steven Klass"
__date__ = "4/19/13 6:22 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)
User = get_user_model()


def fasttracksubmission_factory(create_distribution=True, **kwargs):
    """Generates a basic IncentiveDistribution as if previously submitted to the FastTrack API."""
    project_id = kwargs.pop("project_id", random.randint(0, 5000000))

    if create_distribution:
        distribution = basic_pending_builder_incentive_distribution_factory(**kwargs)
        home_status = distribution.ippitem_set.all()[0].home_status
    else:
        home_status = certified_home_with_basic_eep_factory(**kwargs)

    create_kwargs = {
        "project_id": project_id,
        "home_status": home_status,
        "eps_score": 72,
        "eps_score_built_to_code_score": 94,
        "percent_improvement": 0.23,
        "builder_incentive": 1825.00,
        "rater_incentive": 456.25,
        "carbon_score": 7.7,
        "carbon_built_to_code_score": 9.6,
        "estimated_annual_energy_costs": 1433.56,
        "estimated_monthly_energy_costs": 119.46,
        "similar_size_eps_score": 131,
        "similar_size_carbon_score": 11.4,
    }
    submission = FastTrackSubmission.objects.create(**create_kwargs)
    return submission


def eto_mocked_soap_responses(*args, **kwargs):
    """This will replace out the mocked responses"""

    class MockResponse:
        """Fake Response"""

        def __init__(self, response_content, status_code=200, text="Something"):
            self.content = bytes(response_content.encode("utf8"))
            self.status_code = status_code
            self.text = text

        def raise_for_status(self):
            """Raises stored :class:`HTTPError`, if one occurred."""
            if 400 <= self.status_code < 600:
                raise HTTPError("err", hdrs=None, code=self.status_code, fp=None, msg=self)

    data = kwargs.get("data")
    if data is None:
        # Testing out retrieve_file
        return MockResponse(data)

    data = data if data else ""
    project_id = xmltodict.parse(data)["soap:Envelope"]["soap:Body"]["FTImportXML"]["xmlIn"][
        "ETOImport"
    ]["Project"]["@ID"]
    response = {
        "soap:Envelope": {
            "@xmlns:soap": "http://schemas.xmlsoap.org/soap/envelope/",
            "@xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "@xmlns:xsd": "http://www.w3.org/2001/XMLSchema",
            "soap:Body": {
                "FTImportXMLResponse": {
                    "@xmlns": "http://tempuri.org/",
                    "FTImportXMLResult": {
                        "ImportResponse": {
                            "@xmlns": "",
                            "result": {
                                "code": "SUCCESS",
                                "desc": "All Processed",
                                "projects": {"project": {"@ID": "182609", "#text": "OK"}},
                            },
                            "confirmation": {
                                "projects": {"project": {"@ID": "182609", "#text": "d6193eee"}}
                            },
                            "internalid": {
                                "projects": {
                                    "project": {
                                        "@ID": "182609",
                                        "#text": f"P{project_id.zfill(11)}",
                                    }
                                }
                            },
                        }
                    },
                }
            },
        }
    }
    if "BAD_API" in data:
        response_1 = {
            "soap:Envelope": {
                "@xmlns:soap": "http://schemas.xmlsoap.org/soap/envelope/",
                "@xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
                "@xmlns:xsd": "http://www.w3.org/2001/XMLSchema",
                "soap:Body": {
                    "FTImportXMLResponse": {
                        "@xmlns": "http://tempuri.org/",
                        "FTImportXMLResult": {
                            "ImportResponse": {
                                "@xmlns": "",
                                "result": {
                                    "code": "ERROR",
                                    "desc": "Unexpected Error: The requested ETOV2Service endpoint failed. Review the request and the status code for more error information. This issue caused a database rollback. No data was saved in the database.",
                                    "projects": None,
                                },
                                "confirmation": {"projects": None},
                                "internalid": {"projects": None},
                            }
                        },
                    }
                },
            }
        }
        response_2 = {
            "soap:Envelope": {
                "@xmlns:soap": "http://schemas.xmlsoap.org/soap/envelope/",
                "@xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
                "@xmlns:xsd": "http://www.w3.org/2001/XMLSchema",
                "soap:Body": {
                    "FTImportXMLResponse": {
                        "@xmlns": "http://tempuri.org/",
                        "FTImportXMLResult": {
                            "ImportResponse": {
                                "@xmlns": "",
                                "result": {
                                    "code": "ERROR",
                                    "desc": "Nothing found to processed",
                                    "projects": None,
                                },
                                "confirmation": {"projects": None},
                                "internalid": {"projects": None},
                            }
                        },
                    }
                },
            }
        }
        response = random.choice([response_1, response_2])
        return MockResponse(xmltodict.unparse(response), status_code=400)

    return MockResponse(xmltodict.unparse(response))
