"""App configs."""

__author__ = "Autumn Valenta"
__date__ = "10/10/2018 5:00 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]

import datetime

from django.conf import settings

from axis.core import customers
from infrastructure.utils import symbol_by_name
from .city_of_hillsboro import CityOfHillsboroConfig

settings = getattr(settings, "CUSTOMER_ETO", {})


class CustomerETOConfig(customers.CustomerAppConfig):
    """Main AppConfig settings for customer_eto."""

    name = "axis.customer_eto"
    CUSTOMER_SLUG = "eto"

    extensions = customers.CustomerAppConfig.extensions + (CityOfHillsboroConfig,)

    USE_LEGACY_SIMULATION = True
    ANALYTICS_MIN_THRESHOLD = 100

    ETO_2021_WA_AVAILABLE_DATE = settings.get(
        "ETO_2021_WA_AVAILABLE_DATE", datetime.date(2021, 10, 1)
    )
    ETO_2021_NON_WA_AVAILABLE_DATE = settings.get(
        "ETO_2021_NON_WA_AVAILABLE_DATE", datetime.date(2022, 2, 1)
    )

    PRE_2021_PROGRAMS = [
        "eto",
        "eto-2015",
        "eto-2016",
        "eto-2017",
        "eto-2018",
        "eto-2019",
        "eto-2020",
    ]

    PROJECT_TRACKER_COMPANY_ABBREVIATIONS = {
        # Abbreviations provided by Crystal over email.
        # Our database might have variations on names, so some items are duplicated and map to the same
        # abbreviation.  (See "NW Natural" and "Cascade Natural Gas")
        "avista": "AVI",
        "cascade-gas": "CNG",
        "central-electric": "CNGCEC",
        "clark-pud": "NWNWACLK",
        "idaho-power": "CNGIDP",
        "nw-natural-gas": "NWN",
        "pacific-power": "PAC",
        "portland-electric": "PGE",
        "utility-avista": "AVI",
        "utility-blachly-lane-county-co-op": "NWNBLE",
        "utility-canby-utility-board": "NWNCUB",
        "utility-central-lincoln-pud": "NWNCLP",
        "utility-city-of-ashland": "COA",
        "utility-city-of-bandon": "COB",
        "utility-city-of-cascade-locks": "COCL",
        "utility-city-of-drain": "COD",
        "utility-clatskanie-pud": "NWNCPUD",
        "utility-clearwater-power-company": "CLWP",
        "utility-columbia-basin-electric-co-op": "CBE",
        "utility-columbia-power-co-op": "CPC",
        "utility-columbia-rea": "NWNCR",
        "utility-columbia-river-pud": "NWNCRP",
        "utility-consumers-power-inc": "CPCRV",
        "utility-coos-curry-electric-co-op": "NWNCCEC",
        "utility-douglas-electric-cooperative": "NWNDEC",
        "utility-emerald-pud": "NWNEPUD",
        "utility-forest-grove-light-department": "NWNFGLP",
        "utility-harney-electric-co-op": "HEC",
        "utility-hermiston-energy-services": "CNGHES",
        "utility-hood-river-electric-co-op": "HRE",
        "utility-klickitat-county-pud-no-1": "NWNWAKLI",
        "utility-lane-electric-co-op": "NWNLEC",
        "utility-mcminnville-water-light": "NWNMWL",
        "utility-midstate-electric-cooperative-inc": "CNGME",
        "utility-milton-freewater-light-power": "CNGMFW",
        "utility-monmouth-power-light": "NWNCOM",
        "utility-northern-wasco-county-pud": "NWCPUD",
        "utility-oregon-trail-electric-co-op": "CNGOTE",
        "utility-salem-electric": "NWNSE",
        "utility-skamania-county-pud-no-1": "NWNWASKA",
        "utility-springfield-utility-board": "NWNSUB",
        "utility-surprise-valley-electric-corp": "SVE",
        "utility-tillamook-pud": "TPUD",
        "utility-umatilla-electric-co-op": "CNGUMA",
        "utility-wasco-electric-co-op": "WEC",
        "utility-west-oregon-electric-co-op": "WOE",
        "N/A": "N/A",
    }

    LEGACY_EPS_REPORT_CUTOFF_DATE = settings.get(
        "LEGACY_EPS_REPORT_CUTOFF_DATE", datetime.date(2022, 10, 28)
    )

    DOCUSIGN_USER_ID = "35ba1bab-9820-4674-bbb9-918a20237d2f"
    DOCUSIGN_ACCOUNT_ID = "6203629b-387c-46d2-8556-bd44c38dba0f"

    @property
    def eep_programs(self):
        """Supported programs for program builder"""
        return [
            symbol_by_name(f"{self.name}.eep_programs:Eto2018"),
            symbol_by_name(f"{self.name}.eep_programs:Eto2019"),
            symbol_by_name(f"{self.name}.eep_programs:Eto2020"),
            symbol_by_name(f"{self.name}.eep_programs:Eto2021"),
            symbol_by_name(f"{self.name}.eep_programs:WashingtonCodeCreditProgram"),
            symbol_by_name(f"{self.name}.eep_programs:FireRebuild2021"),
            symbol_by_name(f"{self.name}.eep_programs:Eto2022"),
        ]

    @property
    def analytic_definitions(self):
        """Supported analytics"""
        return [
            {
                "program": "eto-2019",
                "definition": "./analytics/definitions/eto_2019.json",
            },
            {
                "program": "eto-2020",
                "definition": "./analytics/definitions/eto_2020.json",
            },
            {
                "program": "eto-2021",
                "definition": "./analytics/definitions/eto_2021.json",
            },
            {
                "program": "washington-code-credit",
                "definition": "./analytics/definitions/washington_code_credit.json",
            },
            {
                "program": "eto-fire-2021",
                "definition": "./analytics/definitions/eto_fire_2021.json",
            },
            {
                "program": "eto-2022",
                "definition": "./analytics/definitions/eto_2022.json",
            },
        ]


ETO_GEN_3_SLUGS = ["eto-2021", "eto-fire-2021", "eto-2022"]


class UserTestingConfig(CustomerETOConfig):
    """Alternate base config that enables selected test companies."""

    CITY_OF_HILLSBORO_PARTICIPANT_SLUGS = (
        "four-walls-inc",
        "rater-clearesult-rater-eto",
    )
