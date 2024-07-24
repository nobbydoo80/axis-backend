"""test_program_requirements.py: Django """
import datetime
import logging
import unittest
from unittest import mock

from django.apps import apps
from django.test.client import RequestFactory
from django.urls import reverse

from axis.community.tests.factories import community_factory
from axis.company.tests.factories import builder_organization_factory
from axis.core.tests.factories import builder_admin_factory
from axis.core.tests.testcases import AxisTestCase
from axis.filehandling.tests.docusign_mocks import DocusignMock
from axis.home.tests.factories import home_factory
from axis.home.utils import flatten_inheritable_settings
from axis.subdivision.tests.factories import subdivision_factory
from ..models import PermitAndOccupancySettings

__author__ = "Autumn Valenta"
__date__ = "2019-42-03 07:42 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)
app = apps.get_app_config("customer_eto")


class CityOfHillsboroTests(AxisTestCase):
    """Test various pages and APIs for Building Permit and Certificate of Occupancy features."""

    # The specific company isn't important so long as it appears in the enabled list
    TEST_AS = None
    if app.CITY_OF_HILLSBORO_PARTICIPANT_SLUGS:
        TEST_AS = app.CITY_OF_HILLSBORO_PARTICIPANT_SLUGS[0]

    def setUp(self):
        """Provide testing objects."""

        self.company = builder_organization_factory(slug=self.TEST_AS)
        self.user = builder_admin_factory(company=self.company)
        self.client.force_login(self.user)

        self.community_reeds_crossing = community_factory(slug="reeds-crossing")
        self.community_rosedale_parks = community_factory(slug="rosedale-parks")
        self.subdivision_reeds_crossing = subdivision_factory(
            slug="example-reeds-crossing",
            community=self.community_reeds_crossing,
            builder_org=self.company,
        )
        self.subdivision_rosedale_parks = subdivision_factory(
            slug="example-rosedale-parks",
            community=self.community_rosedale_parks,
            builder_org=self.company,
        )
        self.home_reeds_crossing = home_factory(subdivision=self.subdivision_reeds_crossing)
        self.home_rosedale_parks = home_factory(subdivision=self.subdivision_rosedale_parks)

    def test_builder_can_edit_subdivision_compliance_option(self):
        """Test presence of page helper."""

        from axis.subdivision.views.examine import SubdivisionExamineMachinery

        response = self.client.get("/examine/subdivision/subdivision_detail.html")
        self.assertContains(response, "Edit Compliance Option")

        request = RequestFactory().get("/")  # location not important
        request.user = self.user
        instance = self.subdivision_reeds_crossing
        machinery = SubdivisionExamineMachinery(instance, context={"request": request})
        machinery.configure_for_instance(instance)
        helpers = machinery.get_helpers(instance)
        self.assertIn("permitandoccupancysettings", helpers)

    def test_builder_can_edit_home_compliance_option(self):
        """Test presence of page helper."""

        from axis.home.views.machineries import HomeExamineMachinery

        response = self.client.get("/examine/home/home_detail.html")
        self.assertContains(response, "Edit Compliance Option")

        request = RequestFactory().get("/")  # location not important
        request.user = self.user
        instance = self.home_reeds_crossing
        machinery = HomeExamineMachinery(instance, context={"request": request})
        machinery.configure_for_instance(instance)
        helpers = machinery.get_helpers(instance)
        self.assertIn("permitandoccupancysettings", helpers)

    def test_save_subdivision_compliance_option(self):
        """Verify that a compliance option via the source's API is committed in the db."""
        response = self.client.post(
            reverse(
                "apiv2:subdivision-eto-compliance-option",
                kwargs={"pk": self.subdivision_reeds_crossing.pk},
            ),
            {"reeds_crossing_compliance_option": "eps_30"},
        )
        self.assertEqual(response.status_code, 200)
        settings_obj = (
            self.subdivision_reeds_crossing.permitandoccupancysettings_set.get_for_company(
                self.company
            )
        )
        self.assertEqual(settings_obj.reeds_crossing_compliance_option, "eps_30")

    def test_save_home_compliance_option(self):
        """Verify that a compliance option via the source's API is committed in the db."""
        response = self.client.post(
            reverse("apiv2:home-eto-compliance-option", kwargs={"pk": self.home_reeds_crossing.pk}),
            {"reeds_crossing_compliance_option": "eps_40"},
        )
        self.assertEqual(response.status_code, 200)
        settings_obj = self.home_reeds_crossing.permitandoccupancysettings_set.get_for_company(
            self.company
        )
        self.assertEqual(settings_obj.reeds_crossing_compliance_option, "eps_40")

    def test_unset_subdivision_option_inherits_from_company(self):
        """Verify that a missing subdivision option defers to higher up one."""
        company_settings = self.company.permitandoccupancysettings_set.create(
            owner=self.company, company=self.company, reeds_crossing_compliance_option="eps_20"
        )
        result = flatten_inheritable_settings(
            self.company,
            manager_attr="permitandoccupancysettings_set",
            sources=[self.company, self.subdivision_reeds_crossing],
        )
        self.assertEqual(
            result["reeds_crossing_compliance_option"],
            company_settings.reeds_crossing_compliance_option,
        )

    def test_unset_home_option_inherits_from_subdivision(self):
        """Verify that a missing home option defers to higher up one."""
        self.company.permitandoccupancysettings_set.create(
            owner=self.company, company=self.company, reeds_crossing_compliance_option="eps_20"
        )
        subdivision_settings = (
            self.subdivision_reeds_crossing.permitandoccupancysettings_set.create(
                owner=self.company,
                subdivision=self.subdivision_reeds_crossing,
                reeds_crossing_compliance_option="eps_30",
            )
        )
        result = flatten_inheritable_settings(
            self.company,
            manager_attr="permitandoccupancysettings_set",
            sources=[self.company, self.subdivision_reeds_crossing, self.home_reeds_crossing],
        )
        self.assertEqual(
            result["reeds_crossing_compliance_option"],
            subdivision_settings.reeds_crossing_compliance_option,
        )

    def test_null_subdivision_option_inherits_from_company(self):
        """Verify that an explicitly NULL subdivision option defers to higher up one."""
        company_settings = self.company.permitandoccupancysettings_set.create(
            owner=self.company, company=self.company, reeds_crossing_compliance_option="eps_20"
        )
        self.subdivision_reeds_crossing.permitandoccupancysettings_set.create(
            owner=self.company,
            subdivision=self.subdivision_reeds_crossing,
            reeds_crossing_compliance_option=None,
        )
        result = flatten_inheritable_settings(
            self.company,
            manager_attr="permitandoccupancysettings_set",
            sources=[self.company, self.subdivision_reeds_crossing],
        )
        self.assertEqual(
            result["reeds_crossing_compliance_option"],
            company_settings.reeds_crossing_compliance_option,
        )

    def test_null_home_option_inherits_from_subdivision(self):
        """Verify that an explicitly NULL home option defers to higher up one."""
        self.company.permitandoccupancysettings_set.create(
            owner=self.company, company=self.company, reeds_crossing_compliance_option="eps_20"
        )
        subdivision_settings = (
            self.subdivision_reeds_crossing.permitandoccupancysettings_set.create(
                owner=self.company,
                subdivision=self.subdivision_reeds_crossing,
                reeds_crossing_compliance_option="eps_30",
            )
        )
        self.home_reeds_crossing.permitandoccupancysettings_set.create(
            owner=self.company, home=self.home_reeds_crossing, reeds_crossing_compliance_option=None
        )
        result = flatten_inheritable_settings(
            self.company,
            manager_attr="permitandoccupancysettings_set",
            sources=[self.company, self.subdivision_reeds_crossing, self.home_reeds_crossing],
        )
        self.assertEqual(
            result["reeds_crossing_compliance_option"],
            subdivision_settings.reeds_crossing_compliance_option,
        )

    @mock.patch("axis.customer_eto.docusign.BuildingPermit.create_envelope")
    def test_first_signing_stores_unsigned_permit_customer_document(self, bc_env):
        """Document should be created and docusign tracking info saved in the settings data."""
        bc_env.return_value = DocusignMock().create_envelope
        settings_obj = self.home_reeds_crossing.permitandoccupancysettings_set.create(
            owner=self.company,
            home=self.home_reeds_crossing,
            reeds_crossing_compliance_option="eps_20",
        )
        expected_document = self.home_reeds_crossing.customer_documents.filter(
            description=app.OCCUPANCY_DESCRIPTION
        ).first()
        self.assertEqual(expected_document, None)
        self.client.get(
            reverse(
                "apiv2:home-eto-compliance-document", kwargs={"pk": self.home_reeds_crossing.pk}
            )
        )
        settings_obj = self.home_reeds_crossing.permitandoccupancysettings_set.get(
            pk=settings_obj.pk
        )
        expected_document = self.home_reeds_crossing.customer_documents.filter(
            description=app.PERMIT_DESCRIPTION
        ).first()
        self.assertNotEqual(expected_document, None)
        self.assertIn("building_permit", settings_obj.data)
        self.assertIn("envelope_id", settings_obj.data["building_permit"])
        self.assertIn("initial_request_date", settings_obj.data["building_permit"])

    @mock.patch("axis.customer_eto.docusign.BuildingPermit.create_envelope")
    def test_should_get_latest_docusign_status(self, bc_env):
        """Document should be created and docusign tracking info saved in the settings data."""
        bc_env.return_value = DocusignMock().create_envelope
        settings_obj = self.home_reeds_crossing.permitandoccupancysettings_set.create(
            owner=self.company,
            home=self.home_reeds_crossing,
            reeds_crossing_compliance_option="eps_20",
        )
        expected_document = self.home_reeds_crossing.customer_documents.filter(
            description=app.OCCUPANCY_DESCRIPTION
        ).first()
        self.assertEqual(expected_document, None)
        self.client.get(
            reverse(
                "apiv2:home-eto-compliance-document", kwargs={"pk": self.home_reeds_crossing.pk}
            )
        )
        settings_obj = self.home_reeds_crossing.permitandoccupancysettings_set.get(
            pk=settings_obj.pk
        )
        self.assertIn("building_permit", settings_obj.data)
        self.assertIn("envelope_id", settings_obj.data["building_permit"])
        self.assertIn("initial_request_date", settings_obj.data["building_permit"])

        self.assertTrue(settings_obj.should_get_latest_docusign_status("FOOBAR"))
        self.assertTrue(settings_obj.should_get_latest_docusign_status("building_permit"))

        # Now let's hack in the data I need
        def set_date(obj, initial_date, sent_date):
            init_str = initial_date.strftime("%Y-%m-%dT%H:%M:%S.%f") + "0Z"
            sent_str = sent_date.strftime("%Y-%m-%dT%H:%M:%S.%f") + "0Z"
            obj.data["building_permit"].update(
                {
                    "initial_request_date": init_str,
                    "latest_result": {"source": {"sentDateTime": sent_str}},
                }
            )
            obj.save()
            obj.refresh_from_db()
            return obj

        today = datetime.datetime.today()
        initial = datetime.datetime(today.year, today.month, today.day, 1, 0, 0).replace(
            tzinfo=datetime.timezone.utc
        )
        with self.subTest("> 45 days"):
            settings_obj = set_date(
                settings_obj,
                initial - datetime.timedelta(days=46),
                initial - datetime.timedelta(days=44),
            )
            self.assertFalse(settings_obj.should_get_latest_docusign_status())

        with self.subTest("> 30 days"):
            settings_obj = set_date(settings_obj, initial - datetime.timedelta(days=31), initial)
            self.assertFalse(settings_obj.should_get_latest_docusign_status())
            settings_obj = set_date(
                settings_obj,
                initial - datetime.timedelta(days=31),
                initial - datetime.timedelta(days=8),
            )
            self.assertTrue(settings_obj.should_get_latest_docusign_status())

        with self.subTest("> 7 days"):
            settings_obj = set_date(settings_obj, initial - datetime.timedelta(days=8), initial)
            self.assertFalse(settings_obj.should_get_latest_docusign_status())
            settings_obj = set_date(
                settings_obj,
                initial - datetime.timedelta(days=8),
                initial - datetime.timedelta(hours=25),
            )
            self.assertTrue(settings_obj.should_get_latest_docusign_status())

        with self.subTest("> 1days"):
            settings_obj = set_date(settings_obj, initial - datetime.timedelta(days=8), initial)
            self.assertFalse(settings_obj.should_get_latest_docusign_status())
            settings_obj = set_date(
                settings_obj,
                initial - datetime.timedelta(days=1),
                initial - datetime.timedelta(hours=13),
            )
            self.assertTrue(settings_obj.should_get_latest_docusign_status())

        with self.subTest("> 3 hours"):
            settings_obj = set_date(settings_obj, initial - datetime.timedelta(hours=4), initial)
            now = initial + datetime.timedelta(minutes=182)
            self.assertTrue(settings_obj.should_get_latest_docusign_status(now=now))

            settings_obj = set_date(
                settings_obj,
                initial - datetime.timedelta(minutes=179),
                initial + datetime.timedelta(minutes=2),
            )
            self.assertFalse(settings_obj.should_get_latest_docusign_status(now=now))

    @mock.patch("axis.customer_eto.docusign.BuildingPermit.create_envelope")
    @mock.patch("axis.customer_eto.docusign.CertificateOfOccupancy.create_envelope")
    def test_second_signing_stores_unsigned_occupancy_customer_document(self, cc_env, bc_env):
        """Document should be created and docusign tracking info saved in the settings data."""
        cc_env.return_value = DocusignMock().create_envelope
        bc_env.return_value = DocusignMock().create_envelope

        settings_obj = self.home_reeds_crossing.permitandoccupancysettings_set.create(
            owner=self.company,
            home=self.home_reeds_crossing,
            reeds_crossing_compliance_option="eps_30",
        )

        # Set up and fake completion of first signing
        self.client.get(
            reverse(
                "apiv2:home-eto-compliance-document", kwargs={"pk": self.home_reeds_crossing.pk}
            )
        )
        permit_document = self.home_reeds_crossing.customer_documents.filter(
            description=app.PERMIT_DESCRIPTION
        ).first()
        settings_obj = self.home_reeds_crossing.permitandoccupancysettings_set.get(
            pk=settings_obj.pk
        )
        settings_obj.signed_building_permit = permit_document
        settings_obj.save()

        # Continue with second signing
        expected_document = self.home_reeds_crossing.customer_documents.filter(
            description=app.OCCUPANCY_DESCRIPTION
        ).first()
        self.assertEqual(expected_document, None)
        self.client.get(
            reverse(
                "apiv2:home-eto-compliance-document", kwargs={"pk": self.home_reeds_crossing.pk}
            )
        )
        settings_obj = self.home_reeds_crossing.permitandoccupancysettings_set.get(
            pk=settings_obj.pk
        )

        expected_document = self.home_reeds_crossing.customer_documents.filter(
            description=app.OCCUPANCY_DESCRIPTION
        ).first()
        self.assertNotEqual(expected_document, None)
        self.assertIn("certificate_of_occupancy", settings_obj.data)
        self.assertIn("envelope_id", settings_obj.data["certificate_of_occupancy"])
        self.assertIn("initial_request_date", settings_obj.data["certificate_of_occupancy"])

    @mock.patch("axis.customer_eto.docusign.BuildingPermit.create_envelope")
    def test_second_signing_is_blocked_if_first_signing_is_not_finished(self, bc_env):
        """Document should be created and docusign tracking info saved in the settings data."""
        bc_env.return_value = DocusignMock().create_envelope
        self.home_reeds_crossing.permitandoccupancysettings_set.create(
            owner=self.company,
            home=self.home_reeds_crossing,
            reeds_crossing_compliance_option="eps_30",
        )

        # Set up first signing (but leave it unfinished)
        self.client.get(
            reverse(
                "apiv2:home-eto-compliance-document", kwargs={"pk": self.home_reeds_crossing.pk}
            )
        )

        # Second identical signing request should fail
        with self.assertRaisesMessage(ValueError, "You need a signed permit to proceed"):
            self.client.get(
                reverse(
                    "apiv2:home-eto-compliance-document", kwargs={"pk": self.home_reeds_crossing.pk}
                )
            )

    @mock.patch(
        "axis.customer_eto.apps.UserTestingConfig.CITY_OF_HILLSBORO_PARTICIPANT_SLUGS", [TEST_AS]
    )
    def test_subdivision_serializer_has_hillsboro_fields(self):
        """Initialize and inspect the fields on other serializers to ensure they are available."""

        from axis.subdivision.serializers import SubdivisionSerializer

        request = RequestFactory().get("/")  # location not important
        request.user = self.user

        serializer = SubdivisionSerializer(
            instance=self.subdivision_reeds_crossing, context={"request": request}
        )
        self.assertIn("reeds_crossing_compliance_option", list(serializer.fields.keys()))
        self.assertNotIn("rosedale_parks_compliance_option", list(serializer.fields.keys()))

        serializer = SubdivisionSerializer(
            instance=self.subdivision_rosedale_parks, context={"request": request}
        )
        self.assertNotIn("reeds_crossing_compliance_option", list(serializer.fields.keys()))
        self.assertIn("rosedale_parks_compliance_option", list(serializer.fields.keys()))

    @mock.patch(
        "axis.customer_eto.apps.UserTestingConfig.CITY_OF_HILLSBORO_PARTICIPANT_SLUGS", [TEST_AS]
    )
    def test_home_serializer_has_hillsboro_fields(self):
        """Initialize and inspect the fields on other serializers to ensure they are available."""

        from axis.home.serializers import HomeSerializer

        request = RequestFactory().get("/")  # location not important
        request.user = self.user

        serializer = HomeSerializer(instance=self.home_reeds_crossing, context={"request": request})
        self.assertIn("reeds_crossing_compliance_option", list(serializer.fields.keys()))
        self.assertNotIn("rosedale_parks_compliance_option", list(serializer.fields.keys()))

        serializer = HomeSerializer(instance=self.home_rosedale_parks, context={"request": request})
        self.assertNotIn("reeds_crossing_compliance_option", list(serializer.fields.keys()))
        self.assertIn("rosedale_parks_compliance_option", list(serializer.fields.keys()))

    def test_manager_returns_scoped_querysets(self):
        """Compare queryset methods to manually created objects."""

        company_settings = self.company.permitandoccupancysettings_set.create(
            owner=self.company, company=self.company
        )
        subdivision_settings = (
            self.subdivision_reeds_crossing.permitandoccupancysettings_set.create(
                owner=self.company, subdivision=self.subdivision_reeds_crossing
            )
        )
        home_settings = self.home_reeds_crossing.permitandoccupancysettings_set.create(
            owner=self.company, home=self.home_reeds_crossing
        )

        self.assertEqual(
            set([company_settings, subdivision_settings, home_settings]),
            set(PermitAndOccupancySettings.objects.filter_by_company(self.company)),
        )
        self.assertEqual(
            set([company_settings, subdivision_settings, home_settings]),
            set(PermitAndOccupancySettings.objects.filter_by_user(self.user)),
        )
        self.assertEqual(
            set([company_settings]),
            set([PermitAndOccupancySettings.objects.get_for_object(self.company, user=self.user)]),
        )
        self.assertEqual(
            set([subdivision_settings]),
            set(
                [
                    PermitAndOccupancySettings.objects.get_for_object(
                        self.subdivision_reeds_crossing, user=self.user
                    )
                ]
            ),
        )
        self.assertEqual(
            set([home_settings]),
            set(
                [
                    PermitAndOccupancySettings.objects.get_for_object(
                        self.home_reeds_crossing, user=self.user
                    )
                ]
            ),
        )
