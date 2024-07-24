"""seed.py - simulation"""

__author__ = "Steven K"
__date__ = "3/19/21 12:36"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import datetime
import logging

from django.apps import apps
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from rest_framework import status

from simulation.tests.factories import (
    random_name,
    ekotrope_simulation_seed_factory,
    rem_simulation_seed_factory,
    seed_factory,
)
from simulation.enumerations import SourceType, SeedStatus
from simulation.models import Simulation
from simulation.tasks import convert_seed

from axis.company.tests.factories import rater_organization_factory
from axis.core.tests.testcases import ApiV3Tests
from axis.ekotrope.models import Project as EkoProject
from axis.remrate_data.models import Building as RemBuilding, Simulation as RemSimulation

log = logging.getLogger(__name__)

User = get_user_model()
simulation_app = apps.get_app_config("simulation")


class SeedViewSetTests(ApiV3Tests):
    def test_list_protected(self):
        """Can't get to this without auth"""
        url = reverse_lazy("api_v3:simulation-seeds-list")
        response = self.client.get(url, format="json")
        data = response.data

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            "{url}: Unexpected status code {response.status_code}: {data}".format(**locals()),
        )

    def test_detail_protected(self):
        """Can't get to this without auth"""

        user = User.objects.get_or_create(
            company=rater_organization_factory(),
            username=random_name(),
            is_company_admin=True,
        )[0]

        seed = rem_simulation_seed_factory(company=user.company)

        url = reverse_lazy("api_v3:simulation-seeds-detail", args=[seed.pk])
        response = self.client.get(url, format="json")
        data = response.data

        # I shouldn't be able to access others stuff
        user = User.objects.get_or_create(
            company=rater_organization_factory(),
            is_staff=False,
            is_superuser=False,
            username=random_name(),
            is_company_admin=True,
        )[0]
        rem_simulation_seed_factory(company=user.company)

        self.client.force_authenticate(user=user)
        response = self.client.get(url, format="json")
        data = response.data

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
            "{url}: Unexpected status code {response.status_code}: {data}".format(**locals()),
        )

    # def test_rem_serializer_queries(self):
    #     from django.conf import settings
    #     from django.db import connection, reset_queries
    #
    #     user = User.objects.get_or_create(
    #         company=rater_organization_factory(),
    #         username=random_name(),
    #         is_company_admin=True,
    #     )[0]
    #
    #     seed = rem_simulation_seed_factory(company=user.company)
    #     convert_seed(seed.id)
    #
    #     url = reverse_lazy("api_v3:simulation-seeds-list")
    #     self.client.force_authenticate(user=user)
    #
    #     reset_queries()
    #
    #     num_of_expected_queries = 1
    #     try:
    #         settings.DEBUG = True
    #         response = self.client.get(url, format="json")
    #         # print(len(connection.queries))
    #         # import sqlparse
    #         # for query in connection.queries:
    #         #     print(sqlparse.format(query['sql'], reindent=True, keyword_case='upper'))
    #         #     print()
    #         # print(json.dumps(response.data, indent=4))
    #         # print(len(connection.queries))
    #         #
    #         self.assertEqual(len(connection.queries), num_of_expected_queries)
    #     finally:
    #         settings.DEBUG = False
    #         reset_queries()

    # def test_eko_serializer_queries(self):
    #     from django.conf import settings
    #     from django.db import connection, reset_queries
    #
    #     user = User.objects.get_or_create(
    #         company=rater_organization_factory(),
    #         username=random_name(),
    #         is_company_admin=True,
    #     )[0]
    #
    #     seed = ekotrope_simulation_seed_factory(company=user.company)
    #     convert_seed(seed.id)
    #
    #     url = reverse_lazy("api_v3:simulation-seeds-list")
    #     self.client.force_authenticate(user=user)
    #
    #     reset_queries()
    #
    #     num_of_expected_queries = 1
    #     try:
    #         settings.DEBUG = True
    #         response = self.client.get(url, format="json")
    #         self.assertEqual(len(response.data["results"]), 1)
    #         self.assertEqual(len(connection.queries), num_of_expected_queries)
    #     finally:
    #         settings.DEBUG = False
    #         reset_queries()

    # def test_multiple_serializer_queries(self):
    #     from django.conf import settings
    #     from django.db import connection, reset_queries
    #
    #     user = User.objects.get_or_create(
    #         company=rater_organization_factory(),
    #         username=random_name(),
    #         is_company_admin=True,
    #     )[0]
    #
    #     seed = ekotrope_simulation_seed_factory(company=user.company)
    #     convert_seed(seed.id)
    #     seed = rem_simulation_seed_factory(company=user.company)
    #     convert_seed(seed.id)
    #
    #     url = reverse_lazy("api_v3:simulation-seeds-list")
    #     self.client.force_authenticate(user=user)
    #
    #     reset_queries()
    #
    #     num_of_expected_queries = 1
    #     try:
    #         settings.DEBUG = True
    #         response = self.client.get(url, format="json")
    #         self.assertEqual(len(response.data["results"]), 2)
    #         self.assertEqual(len(connection.queries), num_of_expected_queries)
    #     finally:
    #         settings.DEBUG = False
    #         reset_queries()

    def test_summary_no_permission(self):
        """Only admin users can see this"""
        user = User.objects.get_or_create(
            company=rater_organization_factory(),
            username=random_name(),
            is_company_admin=True,
            is_staff=False,
        )[0]

        url = reverse_lazy("api_v3:simulation-seeds-summary")
        self.client.force_authenticate(user=user)

        response = self.client.get(url, format="json")
        data = response.data

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            "{url}: Unexpected status code {response.status_code}: {data}".format(**locals()),
        )

    def test_summary_basics(self):
        """Verify the basics for the summary are in place"""
        user = User.objects.get_or_create(
            company=rater_organization_factory(),
            username=random_name(),
            is_company_admin=True,
            is_staff=True,
        )[0]

        url = reverse_lazy("api_v3:simulation-seeds-summary")
        self.client.force_authenticate(user=user)

        response = self.client.get(url, format="json")
        data = response.data

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "{url}: Unexpected status code {response.status_code}: {data}".format(**locals()),
        )

        today = datetime.datetime.now(datetime.timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        yesterday = today - datetime.timedelta(days=1)

        self.assertEqual(data["created_window"]["start_window"], str(yesterday))
        self.assertEqual(data["created_window"]["end_window"], str(today))
        self.assertEqual(data["created_window"]["remrate_sql"], 0)
        self.assertEqual(data["created_window"]["ekotrope"], 0)
        self.assertEqual(data["created_window"]["axis"], 0)
        self.assertEqual(data["created_window"]["failed"], 0)
        self.assertEqual(data["created_window"]["not_replicated"], 0)

        self.assertEqual(data["outstanding"]["remrate_sql"], 0)
        self.assertEqual(data["outstanding"]["ekotrope"], 0)

    def test_summary_remrate_sql(self):
        """Tests out remrate sql status"""
        user = User.objects.get_or_create(
            company=rater_organization_factory(),
            username=random_name(),
            is_company_admin=True,
            is_staff=True,
        )[0]

        url = reverse_lazy("api_v3:simulation-seeds-summary")
        self.client.force_authenticate(user=user)

        today = datetime.datetime.now(datetime.timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        sim_time_old = today - datetime.timedelta(hours=26)
        sim_time = today - datetime.timedelta(hours=12)

        seed = seed_factory(type=SourceType.REMRATE_SQL.value)

        # Get the source and simulation into the window
        RemBuilding.objects.update(created_on=sim_time_old)
        Simulation.objects.update(created_date=sim_time_old)

        response = self.client.get(url, format="json")

        data = response.data

        self.assertEqual(data["created_window"]["remrate_sql"], 0)
        self.assertEqual(data["created_window"]["axis"], 0)
        self.assertEqual(data["outstanding"]["remrate_sql"], 0)

        # Get the source and simulation into the window
        RemBuilding.objects.update(created_on=sim_time)
        Simulation.objects.update(created_date=sim_time)

        response = self.client.get(url, format="json")
        data = response.data
        self.assertEqual(data["created_window"]["remrate_sql"], 1)
        self.assertEqual(data["created_window"]["axis"], 1)

        # Remove the seed so it's now outstanding
        Simulation.objects.all().delete()
        seed.delete()

        response = self.client.get(url, format="json")
        data = response.data

    def test_summary_ekotrope(self):
        """Test for ekotrope replication"""

        user = User.objects.get_or_create(
            company=rater_organization_factory(),
            username=random_name(),
            is_company_admin=True,
            is_staff=True,
        )[0]

        url = reverse_lazy("api_v3:simulation-seeds-summary")
        self.client.force_authenticate(user=user)

        today = datetime.datetime.now(datetime.timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        sim_time_old = today - datetime.timedelta(hours=26)
        sim_time = today - datetime.timedelta(hours=12)

        seed = seed_factory(type=SourceType.EKOTROPE.value)
        EkoProject.objects.update(created_date=sim_time_old)
        Simulation.objects.update(created_date=sim_time_old)

        response = self.client.get(url, format="json")

        data = response.data

        self.assertEqual(data["created_window"]["ekotrope"], 0)
        self.assertEqual(data["created_window"]["axis"], 0)
        self.assertEqual(data["outstanding"]["ekotrope"], 0)

        # Get the source and simulation into the window
        EkoProject.objects.update(created_date=sim_time)
        Simulation.objects.update(created_date=sim_time)

        response = self.client.get(url, format="json")
        data = response.data
        self.assertEqual(data["created_window"]["ekotrope"], 1)
        self.assertEqual(data["created_window"]["axis"], 1)

        # Remove the seed so it's now outstanding
        Simulation.objects.all().delete()
        seed.delete()

        response = self.client.get(url, format="json")
        data = response.data

        self.assertEqual(data["outstanding"]["ekotrope"], 1)

        # Roll the version back so it falls outside of outstanding
        project = EkoProject.objects.get()
        project_data = project.data
        project_data["algorithmVersion"] = "0.0.1"
        project.data = project_data
        project.save()

        response = self.client.get(url, format="json")
        data = response.data

        self.assertEqual(data["outstanding"]["ekotrope"], 0)

    def test_summary_issues(self):
        """Test for failed and not replicated"""
        user = User.objects.get_or_create(
            company=rater_organization_factory(),
            username=random_name(),
            is_company_admin=True,
            is_staff=True,
        )[0]

        url = reverse_lazy("api_v3:simulation-seeds-summary")
        self.client.force_authenticate(user=user)

        today = datetime.datetime.now(datetime.timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        sim_time = today - datetime.timedelta(hours=12)

        seed = seed_factory(type=SourceType.EKOTROPE.value)
        seed.status = SeedStatus.FAILED
        seed.save()

        response = self.client.get(url, format="json")
        data = response.data

        self.assertEqual(data["created_window"]["failed"], 0)
        self.assertEqual(data["created_window"]["not_replicated"], 0)

        seed.created_date = sim_time
        seed.save()

        response = self.client.get(url, format="json")
        data = response.data

        self.assertEqual(data["created_window"]["failed"], 1)
        self.assertEqual(data["created_window"]["not_replicated"], 0)

        seed.status = SeedStatus.NOT_REPLICATED
        seed.save()

        response = self.client.get(url, format="json")
        data = response.data

        self.assertEqual(data["created_window"]["failed"], 0)
        self.assertEqual(data["created_window"]["not_replicated"], 1)
