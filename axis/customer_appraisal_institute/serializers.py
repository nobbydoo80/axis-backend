import logging

from rest_framework import serializers

__author__ = "Michael Jeffrey"
__date__ = "8/8/17 5:11 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Michael Jeffrey",
]

log = logging.getLogger(__name__)


class GEEAGenericData(serializers.Serializer):
    client_file_num = serializers.CharField()
    appraisal_file_num = serializers.CharField()
    client = serializers.CharField()
    subject_property = serializers.CharField()
    completed_by = serializers.CharField()
    completed_title = serializers.CharField()
    completed_date = serializers.CharField()


class GEEAPageOneData(serializers.Serializer):
    city = serializers.CharField()
    state = serializers.CharField()
    zipcode = serializers.CharField()

    indoor_airplus = serializers.CharField()
    watersense = serializers.CharField()
    energy_star = serializers.CharField()
    zero_energy_ready_home = serializers.CharField()

    ngbs_bronze = serializers.CharField()
    ngbs_silver = serializers.CharField()
    ngbs_gold = serializers.CharField()
    ngbs_emerald = serializers.CharField()

    living_building_certified = serializers.CharField()
    petal_certification = serializers.CharField()
    phi_low_energy = serializers.CharField()
    enerphit = serializers.CharField()
    passive_house = serializers.CharField()
    phius_2015 = serializers.CharField()

    leed_certified = serializers.CharField()
    leed_silver = serializers.CharField()
    leed_gold = serializers.CharField()
    leed_platinum = serializers.CharField()

    green_certification_other = serializers.CharField()
    green_certification_date_verified_day = serializers.CharField()
    green_certification_date_verified_month = serializers.CharField()
    green_certification_date_verified_year = serializers.CharField()
    green_certification_version = serializers.CharField()
    green_certification_organization_url = serializers.CharField()
    green_certification_verification_reviewed_on_site = serializers.CharField()
    green_certification_verification_attached_to_this_report = serializers.CharField()

    hers_rating = serializers.CharField()
    sampling_rating = serializers.CharField()
    projected_rating = serializers.CharField()
    confirmed_rating = serializers.CharField()

    hers_estimated_energy_savings_per_year = serializers.CharField()
    hers_estimated_energy_savings_per_kwh = serializers.CharField()
    hers_rate_dated_month = serializers.CharField()
    hers_rate_dated_day = serializers.CharField()
    hers_rate_dated_year = serializers.CharField()

    doe_score = serializers.CharField()
    doe_official_score = serializers.CharField()
    doe_unofficial_score = serializers.CharField()
    doe_estimated_energy_savings_per_year = serializers.CharField()
    doe_estimated_energy_savings_per_kwh = serializers.CharField()
    doe_rate_dated_month = serializers.CharField()
    doe_rate_dated_day = serializers.CharField()
    doe_rate_dated_year = serializers.CharField()

    other_energy_score_range_start = serializers.CharField()
    other_energy_score_range_end = serializers.CharField()
    other_energy_score = serializers.CharField()
    other_estimated_energy_savings_per_year = serializers.CharField()
    other_estimated_energy_savings_per_kwh = serializers.CharField()
    other_rate_dated_month = serializers.CharField()
    other_rate_dated_day = serializers.CharField()
    other_rate_dated_year = serializers.CharField()
    other_energy_label_sytem = serializers.CharField()
