"""managers.py: Django customer_neea"""


import logging
from collections import OrderedDict

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.timezone import now

__author__ = "Steven Klass"
__date__ = "10/30/12 4:39 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class NeeaLegacyPartnerManager(models.Manager):
    def filter_by_company(self, company, **kwargs):
        """A way to trim down the list of objects by company"""
        if company.slug == "neea":
            return self.filter(**kwargs).distinct()
        return self.filter(axis_company__company_id=company.id).filter(**kwargs).distinct()

    def filter_by_user(self, user, **kwargs):
        """A way to trim down the list of objects by user"""
        if user.is_superuser:
            return self.filter(**kwargs)
        try:
            kwargs["company"] = user.company
        except AttributeError:
            return self.none()
        return self.filter_by_company(**kwargs)

    def filter_for_utilty(self):
        return self.filter(utility_type__isnull=False).exclude(utility_type="")

    def filter_for_builder(self):
        return self.filter(builder_type__isnull=False)


class NeeaLegacyContactManager(models.Manager):
    def filter_by_company(self, company, **kwargs):
        """A way to trim down the list of objects by company"""
        if company.slug == "neea":
            return self.filter(**kwargs).distinct()
        return self.filter(partner__axis_company__company_id=company.id).filter(**kwargs).distinct()

    def filter_by_user(self, user, **kwargs):
        """A way to trim down the list of objects by user"""
        if user.is_superuser:
            return self.filter(**kwargs)
        try:
            kwargs["company"] = user.company
        except AttributeError:
            return self.none()
        return self.filter_by_company(**kwargs)


class NeeaLegacyHomeManager(models.Manager):
    def filter_by_company(self, company, **kwargs):
        """A way to trim down the list of objects by company"""
        if company.slug == "neea":
            return self.filter(**kwargs).distinct()
        return (
            self.filter(legacyneeapartnertohouse__partner__axis_company__company_id=company.id)
            .filter(**kwargs)
            .distinct()
        )

    def filter_by_user(self, user, **kwargs):
        """A way to trim down the list of objects by user"""
        if user.is_superuser:
            return self.filter(**kwargs)
        try:
            kwargs["company"] = user.company
        except AttributeError:
            return self.none()
        return self.filter_by_company(**kwargs)


class NeeaGeneralLegacyManager(models.Manager):
    def filter_by_company(self, company, **kwargs):
        """A way to trim down the list of objects by company"""
        if company.slug == "neea":
            return self.filter(**kwargs)
        return self.filter(axis_company__company_id=company.id)

    def filter_by_user(self, user, **kwargs):
        """A way to trim down the list of objects by user"""
        if user.is_superuser:
            return self.filter(**kwargs)
        try:
            kwargs["company"] = user.company
        except AttributeError:
            return self.none()
        return self.filter_by_company(**kwargs)


class LegacyNEEAPartnerToHouseManager(NeeaGeneralLegacyManager):
    def get_distinct_partners(self, home):
        """Customer want this in a particular order"""
        from axis.customer_neea.models import (
            LegacyNEEAHome,
            LegacyNEEAPartner,
            LegacyNEEAPartnerToHouse,
        )

        assert isinstance(home, LegacyNEEAHome), "Need a LegacyNEEAHome"
        partner_ids = self.filter(home=home).values_list("partner_id", flat=True)
        partners = LegacyNEEAPartner.objects.filter(id__in=list(set(partner_ids))).order_by(
            "partner_name"
        )
        contacts = LegacyNEEAPartnerToHouse.objects.filter(home=home)
        result = OrderedDict()
        PARTNER_PRIORITY_MAP = [
            {"partner_type": "Builder", "name": "Builder"},
            {"partner_type": "Verifier", "name": "Verifier"},
            {"partner_type": "PerformanceTester", "name": "Performance Tester"},
            {
                "partner_type": "Utility",
                "utility_type": "Electric",
                "name": "Electric Utility",
            },
            {
                "partner_type": "Utility",
                "utility_type": "Both",
                "name": "Electric Utility",
            },
            {"partner_type": "Utility", "utility_type": "Gas", "name": "Gas Utility"},
            {"partner_type": "Company", "name": "General Company"},
        ]

        for priority in PARTNER_PRIORITY_MAP:
            name = priority.pop("name")
            for partner in partners.filter(**priority):
                if name not in result.keys():
                    result[name] = []
                result[name].append(partner)
                for contact in contacts:
                    try:
                        if contact.partner == partner:
                            if contact.contact:
                                if not hasattr(partner, "contacts"):
                                    partner.contacts = []
                                if contact.contact not in partner.contacts:
                                    partner.contacts.append(contact.contact)
                    except ObjectDoesNotExist:
                        continue
        return result


class StandardProtocolCalculatorManager(models.Manager):
    def filter_by_company(self, company, **kwargs):
        """A way to trim down the list of objects by company"""
        from axis.home.models import EEPProgramHomeStatus

        home_stats = list(
            EEPProgramHomeStatus.objects.filter_by_company(company).values_list("id", flat=True)
        )
        return self.filter(home_status_id__in=home_stats)

    def filter_by_user(self, user, **kwargs):
        """A way to trim down the list of objects by user"""
        if user.is_superuser:
            return self.filter(**kwargs)
        try:
            kwargs["company"] = user.company
        except AttributeError:
            return self.none()
        return self.filter_by_company(**kwargs)

    def update_or_create_from_calculator(self, calculator):
        incentive_paying_organization = None
        if calculator.incentives.incentive_paying_organization:
            from axis.company.models import Company

            incentive_paying_organization = Company.objects.filter(
                slug=calculator.incentives.incentive_paying_organization
            ).first()

        estar_front_load_clothes_washer_installed = None
        estar_clothes_washer_installed = calculator.estar_clothes_washer_installed
        estar_std_refrigerators_installed = None
        estar_refrigerators_installed = calculator.estar_refrigerators_installed

        if calculator.program == "neea-bpa":
            estar_front_load_clothes_washer_installed = (
                calculator.estar_front_load_clothes_washer_installed
            )
            estar_clothes_washer_installed = None
            estar_std_refrigerators_installed = calculator.estar_std_refrigerators_installed
            estar_refrigerators_installed = None

        return self.update_or_create(
            home_status=calculator.home_status,
            defaults=dict(
                heating_fuel=calculator.heating_fuel,
                heating_system_config=calculator.heating_system_config,
                home_size=calculator.home_size,
                estar_std_refrigerators_installed=estar_std_refrigerators_installed,
                estar_refrigerators_installed=estar_refrigerators_installed,
                estar_dishwasher_installed=calculator.estar_dishwasher_installed,
                estar_front_load_clothes_washer_installed=estar_front_load_clothes_washer_installed,
                estar_clothes_washer_installed=estar_clothes_washer_installed,
                clothes_dryer_tier=calculator.clothes_dryer_tier,
                cfl_installed=calculator.cfl_installed,
                led_installed=calculator.led_installed,
                total_installed_lamps=calculator.total_installed_lamps,
                smart_thermostat_installed=calculator.smart_thermostat_installed,
                qty_shower_head_1p5=calculator.qty_shower_head_1p5,
                qty_shower_head_1p75=calculator.qty_shower_head_1p75,
                heating_kwh_savings=calculator.heating_kwh_savings,
                heating_therm_savings=calculator.heating_therm_savings,
                cooling_kwh_savings=calculator.cooling_kwh_savings,
                cooling_therm_savings=calculator.cooling_therm_savings,
                smart_thermostat_kwh_savings=calculator.smart_thermostat_kwh_savings,
                smart_thermostat_therm_savings=calculator.smart_thermostat_therm_savings,
                water_heater_kwh_savings=calculator.water_heater_kwh_savings,
                water_heater_therm_savings=calculator.water_heater_therm_savings,
                showerhead_kwh_savings=calculator.showerhead_kwh_savings,
                showerhead_therm_savings=calculator.showerhead_therm_savings,
                lighting_kwh_savings=calculator.lighting_kwh_savings,
                lighting_therm_savings=calculator.lighting_therm_savings,
                appliance_kwh_savings=calculator.appliance_kwh_savings,
                appliance_therm_savings=calculator.appliance_therm_savings,
                total_kwh_savings=calculator.total_kwh_savings,
                total_therm_savings=calculator.total_therm_savings,
                has_incentive=calculator.incentives.has_incentive,
                reference_home_kwh=calculator.incentives.reference_home_kwh,
                busbar_consumption=calculator.incentives.busbar_consumption,
                busbar_savings=calculator.incentives.busbar_savings,
                pct_improvement_method=calculator.incentives.pct_improvement_method,
                percent_improvement=calculator.incentives.default_percent_improvement,
                revised_percent_improvement=calculator.revised_percent_improvement,
                total_incentive=calculator.incentives.total_incentive,
                builder_incentive=calculator.incentives.builder_incentive,
                bpa_hvac_kwh_savings=calculator.incentives.bpa_hvac_kwh_savings,
                hvac_kwh_incentive=calculator.incentives.hvac_kwh_incentive,
                bpa_lighting_kwh_savings=calculator.incentives.bpa_lighting_kwh_savings,
                lighting_kwh_incentive=calculator.incentives.lighting_kwh_incentive,
                bpa_water_heater_kwh_savings=calculator.incentives.bpa_water_heater_kwh_savings,
                water_heater_kwh_incentive=calculator.incentives.water_heater_kwh_incentive,
                bpa_appliance_kwh_savings=calculator.incentives.bpa_appliance_kwh_savings,
                appliance_kwh_incentive=calculator.incentives.appliance_kwh_incentive,
                bpa_showerhead_kwh_savings=calculator.incentives.bpa_showerhead_kwh_savings,
                showerhead_kwh_incentive=calculator.incentives.showerhead_kwh_incentive,
                bpa_windows_shell_kwh_savings=calculator.incentives.bpa_windows_shell_kwh_savings,
                windows_shell_kwh_incentive=calculator.incentives.windows_shell_kwh_incentive,
                bpa_smart_thermostat_kwh_savings=calculator.incentives.bpa_smart_thermostat_kwh_savings,
                smart_thermostat_kwh_incentive=calculator.incentives.smart_thermostat_kwh_incentive,
                reported_shell_windows_kwh_savings=calculator.incentives.reported_shell_windows_kwh_savings,
                reported_shell_windows_incentive=calculator.incentives.reported_shell_windows_incentive,
                reported_hvac_waterheater_kwh_savings=calculator.incentives.reported_hvac_waterheater_kwh_savings,
                reported_hvac_waterheater_incentive=calculator.incentives.reported_hvac_waterheater_incentive,
                reported_lighting_showerhead_tstats_kwh_savings=calculator.incentives.reported_lighting_showerhead_tstats_kwh_savings,
                reported_lighting_showerhead_tstats_incentive=calculator.incentives.reported_lighting_showerhead_tstats_incentive,
                code_total_consumption_mmbtu=calculator.code_data_total_consumption_mmbtu,
                improved_total_consumption_mmbtu=calculator.improved_data_total_consumption_mmbtu,
                improved_total_consumption_mmbtu_with_savings=calculator.improved_total_consumption_mmbtu_with_savings,
                incentive_paying_organization=incentive_paying_organization,
                last_updated=now(),
            ),
        )
