"""strings.py: Django customer_neea"""

import logging
from collections import OrderedDict

__author__ = "Steven Klass"
__date__ = "4/17/14 12:53 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)

# Notification for NEEA
NEEA_MISSING_ASSOCIATION = """
    {company_type_pretty} <a href="{company_list_url}">{company}</a> is associated with
    <a href="{home_url}">{home}</a> with program {program} but is not associated with NEEA.
"""

# Notifications for NEEA-related companies (they can't fix it on their own).
NEEA_NO_UTILITY_RELATIONSHIP = """
    The Utility {company} that you have associated with this home has not been
    approved by NEEA for the {program}. Please contact the Better Built NW team at
    <a href="mailto:info@betterbuiltnw.com">info@betterbuiltnw.com</a> to resolve this issue.
"""

NEEA_NO_HVAC_RELATIONSHIP = """
    The HVAC {company} that you have associated with this home has not been
    approved by NEEA for the {program}. Please contact the Better Built NW team at
    <a href="mailto:info@betterbuiltnw.com">info@betterbuiltnw.com</a> to resolve this issue.
"""

NEEA_NO_BUILDER_RELATIONSHIP = """
    The Builder {company} that you have associated with this home has not been
    approved by NEEA for the {program}. Please contact the Better Built NW team at
    <a href="mailto:info@betterbuiltnw.com">info@betterbuiltnw.com</a> to resolve this issue.
"""

NEEA_BPA_2019_CHECKSUMS = [
    ("C8EDE134", "WA Perf Path Zonal - Small_2019-Final.udr"),
    ("D014F416", "WA Perf Path Zonal - Medium_2019-Final.udr"),
    ("86593E60", "WA Perf Path Zonal - Large_2019-Final.udr"),
    ("208A62B2", "WA Perf Path Central - Small_2019-Final.udr"),
    ("67B73E95", "WA Perf Path Central - Medium_2019-Final.udr"),
    ("C7CF1EB6", "WA Perf Path Central - Large_2019-Final.udr"),
    ("3A9D8804", ("OR Perf Path Zonal 2019-Final.udr", "OR Perf Zonal 2019-Final.udr")),
    ("5FA1D9E5", ("OR Perf Path Central 2019-Final.udr", "OR Central 2019-Final.udr")),
    ("2869C2E5", "MT Perf Path Zonal_2019-Final.udr"),
    ("F9C2FC51", "MT Perf Path Central_2019-Final.udr"),
    ("91DC131E", "ID Perf Path Zonal_2019-Final.udr"),
    ("E23D42E6", "ID Perf Path Central_2019-Final.udr"),
    ("0B94E168", "WA Perf Path Zonal - Small_2020-Final.udr"),
    ("00ABF642", "WA Perf Path Zonal - Medium_2020-Final.udr"),
    ("7F3A3A06", "WA Perf Path Zonal - Large_2020-Final.udr"),
    ("343B924D", "WA Perf Path Central - Small_2020-Final.udr"),
    ("A4E53E30", "WA Perf Path Central - Medium_2020-Final.udr"),
    ("93EFB3BF", "WA Perf Path Central - Large_2020-Final.udr"),
    ("7EFE1FE0", "OR Perf Path Zonal 2020-Final.udr"),
    ("2E07EEEA", "OR Perf Path Central 2020-Final.udr"),
    ("9F4E8AFA", "MT Perf Path Zonal_2020-Final.udr"),
    ("16251C7D", "MT Perf Path Central_2020-Final.udr"),
    ("D8BF655B", "ID Perf Path Zonal_2020-Final.udr"),
    ("1C79E800", "ID Perf Path Central_2020-Final.udr"),
]

NEEA_BPA_2021_CHECKSUMS = [
    ("BF6A0805", "WAPerfPath-GasCentral-GasDHW-Small_2021-Final.udr"),
    ("54A9C108", "WAPerfPath-GasCentral-GasDHW-Medium_2021-Final.udr"),
    ("BADC1B34", "WAPerfPath-GasCentral-GasDHW-Large_2021-Final.udr"),
    ("BB85F2F1", "WAPerfPath-GasCentral-ElecDHW-Small_2021-Final.udr"),
    ("C8A062FC", "WAPerfPath-GasCentral-ElecDHW-Medium_2021-Final.udr"),
    ("816BED6D", "WAPerfPath-GasCentral-ElecDHW-Large_2021-Final.udr"),
    ("D8825E6C", "WAPerfPath-ElecZonal-GasDHW-Small_2021-Final.udr"),
    ("674F2A7C", "WAPerfPath-ElecZonal-GasDHW-Medium_2021-Final.udr"),
    ("638D8EFA", "WAPerfPath-ElecZonal-GasDHW-Large_2021-Final.udr"),
    ("7717E469", "WAPerfPath-ElecZonal-ElecDHW-Small_2021-Final.udr"),
    ("C56FCAB4", "WAPerfPath-ElecZonal-ElecDHW-Medium_2021-Final.udr"),
    ("8A345A59", "WAPerfPath-ElecZonal-ElecDHW-Large_2021-Final.udr"),
    ("C78ECA3B", "WAPerfPath-ElecCentral-GasDHW-Small_2021-Final.udr"),
    ("63B3F27B", "WAPerfPath-ElecCentral-GasDHW-Medium_2021-Final.udr"),
    ("0B48F031", "WAPerfPath-ElecCentral-GasDHW-Large_2021-Final.udr"),
    ("ACBDC731", "WAPerfPath-ElecCentral-ElecDHW-Small_2021-Final.udr"),
    ("AAC905AD", "WAPerfPath-ElecCentral-ElecDHW-Medium_2021-Final.udr"),
    ("92EF7FF6", "WAPerfPath-ElecCentral-ElecDHW-Large_2021-Final.udr"),
    ("5336B197", "OR Perf Path Zonal 2021-Final.udr"),
    ("555A4B54", "OR Perf Path Central 2021-Final.udr"),
    ("5B504267", "ID Perf Path Zonal_2021-Final.udr"),
    ("D509DE18", "ID Perf Path Central_2021-Final.udr"),
    ("A7AF23BC", "OR Perf Path Central 2022-FINAL.udr"),
    ("D6520E37", "OR Perf Path Zonal 2022-FINAL.udr"),
]

WA_CODE_STUDY_POINTS_ASSIGNMENT = OrderedDict(
    [
        (
            "dwelling-type",
            OrderedDict(
                [
                    ("Small Dwelling", 1.5),
                    ("Medium Dwelling", 3.5),
                    ("Large Dwelling", 4.5),
                    # ('Additions', 0.5)
                ]
            ),
        ),
        (
            "efficient-building-envelope",
            OrderedDict(
                [
                    ("Not Applicable", 0),
                    ("1a", 0.5),
                    ("1b", 1.0),
                    ("1c", 2.0),
                    ("1d", 0.5),
                ]
            ),
        ),
        (
            "efficient-building-air-leakage",
            OrderedDict(
                [
                    ("Not Applicable", 0),
                    ("2a", 0.5),
                    ("2b", 1.0),
                    ("2c", 1.5),
                ]
            ),
        ),
        (
            "efficient-building-hvac",
            OrderedDict(
                [
                    ("Not Applicable", 0),
                    ("3a", 1.0),
                    ("3b", 1.0),
                    ("3c", 1.5),
                    ("3d", 1.0),
                ]
            ),
        ),
        (
            "efficient-building-hvac-distribution",
            OrderedDict(
                [
                    ("Not Applicable", 0),
                    ("4", 1.0),
                ]
            ),
        ),
        (
            "efficient-building-water-heating-5a",
            OrderedDict(
                [
                    ("Not Applicable", 0),
                    ("5a", 0.5),
                ]
            ),
        ),
        (
            "efficient-building-water-heating-5bc",
            OrderedDict(
                [
                    ("Not Applicable", 0),
                    ("5b", 1.0),
                    ("5c", 1.5),
                ]
            ),
        ),
        (
            "efficient-building-water-heating-5d",
            OrderedDict(
                [
                    ("Not Applicable", 0),
                    ("5d", 0.5),
                ]
            ),
        ),
        (
            "efficient-building-renewable-energy",
            OrderedDict(
                [
                    ("0", 0),
                    ("1", 0.5),
                    ("2", 1.0),
                    ("3", 1.5),
                    ("4", 2.0),
                    ("5", 2.5),
                ]
            ),
        ),
    ]
)

WA_CODE_DWELLING_TYPES = WA_CODE_STUDY_POINTS_ASSIGNMENT["dwelling-type"].keys()
WA_CODE_BUILDING_ENVELOPE_TYPES = sorted(
    WA_CODE_STUDY_POINTS_ASSIGNMENT["efficient-building-envelope"].keys()
)
WA_CODE_AIR_LEAKAGE = sorted(
    WA_CODE_STUDY_POINTS_ASSIGNMENT["efficient-building-air-leakage"].keys()
)
WA_CODE_BUILDING_HVAC = sorted(WA_CODE_STUDY_POINTS_ASSIGNMENT["efficient-building-hvac"].keys())
WA_CODE_BUILDING_HVAC_DISTRIBUTION = sorted(
    WA_CODE_STUDY_POINTS_ASSIGNMENT["efficient-building-hvac-distribution"].keys()
)
WA_CODE_BUILDING_WATER_HEATING_5A = sorted(
    WA_CODE_STUDY_POINTS_ASSIGNMENT["efficient-building-water-heating-5a"].keys()
)
WA_CODE_BUILDING_WATER_HEATING_5BC = sorted(
    WA_CODE_STUDY_POINTS_ASSIGNMENT["efficient-building-water-heating-5bc"].keys()
)
WA_CODE_BUILDING_WATER_HEATING_5D = sorted(
    WA_CODE_STUDY_POINTS_ASSIGNMENT["efficient-building-water-heating-5d"].keys()
)
WA_CODE_QTY_RENEWABLE_ENERGY = sorted(
    WA_CODE_STUDY_POINTS_ASSIGNMENT["efficient-building-renewable-energy"].keys()
)
WA_CODE_ANNOTATIONS = list(WA_CODE_STUDY_POINTS_ASSIGNMENT.keys()) + ["wa-code-study-score"]
