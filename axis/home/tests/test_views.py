"""tests.py: Django home.tests"""

__author__ = "Steven Klass"
__date__ = "12/5/11 10:50 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

import datetime
import json
import logging
import random
import re
import tempfile
from functools import partial
from unittest import mock

from PIL import Image
from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.forms import model_to_dict
from django.urls import reverse
from django.utils import timezone

from axis.company.models import Company, SponsorPreferences
from axis.core.tests.client import AxisClient
from axis.core.tests.factories import (
    provider_user_factory,
    rater_user_factory,
    SET_NULL,
    builder_user_factory,
)
from axis.core.tests.testcases import (
    AxisTestCase,
    ApiV3Tests,
)
from axis.customer_hirl.models import HIRLProjectRegistration, HIRLProject, BuilderAgreement
from axis.customer_hirl.tests.factories import (
    hirl_project_registration_factory,
    hirl_project_factory,
    builder_agreement_factory,
)
from axis.customer_hirl.tests.mixins import HIRLScoring2020NewConstructionTaskMixin
from axis.eep_program.models import EEPProgram
from axis.eep_program.tests.factories import (
    basic_eep_program_factory,
)
from axis.examine.tests.utils import MachineryDriver
from axis.filehandling.machinery import customerdocument_machinery_factory
from axis.filehandling.models import CustomerDocument
from axis.floorplan.models import Floorplan
from axis.home.models import Home, EEPProgramHomeStatus
from axis.home.views import HomeStatusReportMixin
from axis.home.views.machineries import HomeExamineMachinery, ActiveFloorplanExamineMachinery
from axis.invoicing.tests.factories import invoice_factory
from axis.qa.models import QARequirement, QAStatus
from axis.relationship.models import Relationship
from axis.sampleset.models import SampleSet
from simulation.enumerations import AnalysisEngine, AnalysisType, AnalysisStatus
from simulation.models import simulation
from simulation.tests.factories import simulation_factory, analysis_factory
from simulation.tests.factories.utils import dump_test_data
from .factories import (
    home_photo_factory,
)
from .mixins import CertificationTestMixin, HomeViewTestsMixins, HostStatusReportMixin
from .. import strings
from ..tasks import update_home_states
from ...company.tests.factories import (
    provider_organization_factory,
    builder_organization_factory,
    rater_organization_factory,
    developer_organization_factory,
    architect_organization_factory,
    communityowner_organization_factory,
)
from axis.geocoder.models import Geocode
from axis.geographic.tests.factories import real_city_factory
from axis.messaging.models import Message, MessagingPreference

log = logging.getLogger(__name__)
customer_hirl_app = apps.get_app_config("customer_hirl")
User = get_user_model()


class HomeViewTests(HomeViewTestsMixins, ApiV3Tests):
    """Test out the home app"""

    client_class = AxisClient

    def test_login_required(self):
        """Test that we can't see homes without logging in"""
        stat = EEPProgramHomeStatus.objects.exclude(state="complete")[0]
        url = reverse("home:list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(url, response["Location"], msg=url)
        self.assertIn(reverse("auth:login"), response["Location"])

        url = reverse("home:add")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(url, response["Location"], msg=url)
        self.assertIn(reverse("auth:login"), response["Location"])

        url = reverse("home:view", kwargs={"pk": 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(url, response["Location"], msg=url)
        self.assertIn(reverse("auth:login"), response["Location"])

        url = reverse("home:certify", kwargs={"pk": 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(url, response["Location"], msg=url)
        self.assertIn(reverse("auth:login"), response["Location"])

        url = reverse("home:set_state", kwargs={"pk": stat.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(url, response["Location"], msg=url)
        self.assertIn(reverse("auth:login"), response["Location"])

        url = reverse("home:report:status")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(url, response["Location"], msg=url)
        self.assertIn(reverse("auth:login"), response["Location"])

        url = reverse("home:report:stats_document")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(url, response["Location"], msg=url)
        self.assertIn(reverse("auth:login"), response["Location"])

        url = reverse("home:report:certificate")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(url, response["Location"], msg=url)
        self.assertIn(reverse("auth:login"), response["Location"])

        url = reverse("home:report:checklist")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(url, response["Location"], msg=url)
        self.assertIn(reverse("auth:login"), response["Location"])

        url = reverse("home:report:energy_star_certificate")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(url, response["Location"], msg=url)
        self.assertIn(reverse("auth:login"), response["Location"])

        url = reverse("home:report:legacy_status")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(url, response["Location"], msg=url)
        self.assertIn(reverse("auth:login"), response["Location"])

        url = reverse("home:certified")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(url, response["Location"], msg=url)
        self.assertIn(reverse("auth:login"), response["Location"])

        url = reverse("home:upload")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(url, response["Location"], msg=url)
        self.assertIn(reverse("auth:login"), response["Location"])

    def test_company_user_has_permissions(self):
        """Test that we can login and see homes"""
        user = self.get_admin_user(company_type=["provider"], only_related=True)
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        self.assertEqual(user.has_perm("home.view_home"), True)
        self.assertEqual(user.has_perm("home.change_home"), True)
        self.assertEqual(user.has_perm("home.add_home"), True)
        self.assertEqual(user.has_perm("home.delete_home"), True)

        stat = EEPProgramHomeStatus.objects.filter_by_user(user).exclude(state="complete").first()

        url = reverse("home:list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        url = reverse("home:add")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        url = reverse("home:view", kwargs={"pk": stat.home.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        url = reverse("home:set_state", kwargs={"pk": stat.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        url = reverse("home:report:status")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        url = reverse("home:report:stats_document")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        url = reverse("home:report:certificate")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        url = reverse("home:report:checklist")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        url = reverse("home:report:energy_star_certificate")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        url = reverse("home:report:legacy_status")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        url = reverse("home:certified")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        url = reverse("home:upload")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.assertTrue(stat.is_eligible_for_certification())
        self.assertTrue(stat.can_user_certify(user))
        url = reverse("home:certify", kwargs={"pk": stat.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_list_view(self):
        """Test list view for homes"""
        user = self.admin_user
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        url = reverse("home:list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(url, ajax=True)
        self.assertEqual(response.status_code, 200)

        expected = Home.objects.filter_by_company(user.company, show_attached=True)
        self.assertGreater(expected.count(), 0)
        match_ids = []
        data = json.loads(response.content)["data"]
        for item in data:
            m = re.search(r"\"/home/(\d+)/\"", item.get("0"))
            if m:
                match_ids.append(int(m.group(1)))
        self.assertEqual(set(expected.values_list("id", flat=True)), set(match_ids))

    def test_certify_view_fail_incomplete(self):
        """Tests that the HomeCertifyForm rejects a certification if percentage is < 100"""
        user = self.get_admin_user(company_type="provider")
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        stat = EEPProgramHomeStatus.objects.filter_by_company(user.company, pct_complete__lte=99)[0]
        self.assertEqual(stat.state, "inspection")

        data = {"certification_date": datetime.date.today()}

        url = reverse("home:certify", kwargs={"pk": stat.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 200)
        msg = strings.NOT_ELIGIBLE_FOR_CERTIFICATION.format(
            url=stat.home.get_absolute_url(), home=stat.home, program=stat.eep_program
        )
        # After Django 4.1 use this one
        # self.assertFormError(response.context["form"], field=None, errors=msg)
        self.assertFormError(response, "form", field=None, errors=msg)

    def test_certify_view_eep_requirements(self):
        """Test certification errors based on required program relationships."""
        user = self.get_admin_user(company_type="provider")
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        stat = EEPProgramHomeStatus.objects.filter(
            pct_complete__gte=99.9, certification_date__isnull=True
        )[0]
        # Assert we have a direct relationship
        Relationship.objects.validate_or_create_relations_to_entity(
            entity=user.company, direct_relation=stat.company
        )

        stat.save()
        self.assertEqual(stat.state, "certification_pending")
        self.assertEqual(stat.is_eligible_for_certification(), True)

        # Add in the list of requirements..
        stat.eep_program.require_builder_relationship = True
        stat.eep_program.require_builder_assigned_to_home = True
        stat.eep_program.require_hvac_relationship = True
        stat.eep_program.require_hvac_assigned_to_home = True
        stat.eep_program.require_utility_relationship = True
        stat.eep_program.require_utility_assigned_to_home = True
        stat.eep_program.require_rater_relationship = True
        stat.eep_program.require_rater_assigned_to_home = True
        stat.eep_program.require_provider_relationship = True
        stat.eep_program.require_provider_assigned_to_home = True
        stat.eep_program.require_qa_relationship = True
        stat.eep_program.require_qa_assigned_to_home = True
        stat.eep_program.save()

        stat = EEPProgramHomeStatus.objects.get(id=stat.id)
        self.assertEqual(stat.state, "certification_pending")
        self.assertEqual(stat.is_eligible_for_certification(), False)

        errors = [
            strings.MISSING_QA.format(program=stat.eep_program),
            strings.MISSING_HVAC.format(program=stat.eep_program),
        ]

        issues = stat.report_eligibility_for_certification()
        self.assertEqual(set(errors), set(issues))

        _ct = ContentType.objects.get_for_model(Home)
        stat.home.relationships.all().exclude(company_id=stat.eep_program.owner.id).delete()
        stat = EEPProgramHomeStatus.objects.get(id=stat.id)
        self.assertEqual(stat.state, "certification_pending")
        self.assertEqual(stat.is_eligible_for_certification(), False)

        errors = [
            strings.MISSING_QA.format(program=stat.eep_program),
            strings.MISSING_HVAC.format(program=stat.eep_program),
            strings.MISSING_PROVIDER.format(program=stat.eep_program),
            strings.MISSING_RATER.format(program=stat.eep_program),
            strings.MISSING_UTILITY.format(program=stat.eep_program),
        ]
        issues = stat.report_eligibility_for_certification()
        self.assertEqual(set(errors), set(issues))

    @mock.patch("axis.home.signals.HomeCertifiedMessage.send")
    def test_certify_home_view_pass(self, send_message):
        """Test certifying a home"""
        rater_user = self.get_admin_user(company_type="rater")
        rater_co = rater_user.company
        self.assertTrue(
            self.client.login(username=rater_user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (rater_user.username, rater_user.pk),
        )
        self.assertEqual(rater_user.company.id, rater_co.id)

        stat = EEPProgramHomeStatus.objects.filter_by_company(
            rater_user.company, pct_complete__gte=99.9, certification_date__isnull=True
        )[0]
        stat.save()
        self.assertEqual(stat.state, "certification_pending")

        data = {"certification_date": datetime.date.today()}
        response = self.client.post(reverse("home:certify", kwargs={"pk": stat.id}), data=data)
        self.assertIsNone(EEPProgramHomeStatus.objects.get(id=stat.id).certification_date)
        self.assertEqual(response.status_code, 200)
        msg = strings.FAILED_CERTIFICATION_NOT_ALLOWED_TO_CERTIFY.format(
            url=stat.home.get_absolute_url(), home=stat.home, program=stat.eep_program
        )
        # After Django 4.1 use this one
        # self.assertFormError(response.context["form"], field=None, errors=msg)
        self.assertFormError(response, "form", field=None, errors=msg)

        provider_user = self.get_admin_user(company_type="provider")
        provider_co = provider_user.company
        # Ensure they have a relationship with us..
        self.assertIn(rater_co, Relationship.objects.get_reversed_companies(provider_co))
        # But we don't have a relationship with them..
        Relationship.objects.get(
            company=provider_co,
            content_type=ContentType.objects.get_for_model(Company),
            object_id=rater_co.id,
        ).delete()
        Relationship.objects.get(
            company=rater_co,
            content_type=ContentType.objects.get_for_model(Company),
            object_id=provider_co.id,
        ).delete()

        self.assertNotIn(rater_co, provider_co.relationships.get_companies())
        self.assertNotIn(provider_co, rater_co.relationships.get_companies())

        self.assertTrue(
            self.client.login(username=provider_user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login"
            % (provider_user.username, provider_user.pk),
        )
        response = self.client.post(reverse("home:certify", kwargs={"pk": stat.id}), data=data)
        self.assertIsNone(EEPProgramHomeStatus.objects.get(id=stat.id).certification_date)
        self.assertEqual(response.status_code, 404)  # We have no relationship

        # We need a relationships
        Relationship.objects.validate_or_create_relations_to_entity(
            entity=rater_co, direct_relation=provider_co
        )
        Relationship.objects.validate_or_create_relations_to_entity(
            entity=provider_co, direct_relation=rater_co
        )
        Relationship.objects.validate_or_create_relations_to_entity(
            entity=provider_co, direct_relation=stat.eep_program.owner
        )
        Relationship.objects.validate_or_create_relations_to_entity(
            entity=stat.home, direct_relation=provider_co
        )

        self.assertIn(rater_co, provider_co.relationships.get_companies())
        self.assertIn(provider_co, rater_co.relationships.get_companies())

        self.assertEqual(stat.is_eligible_for_certification(), True)
        response = self.client.post(reverse("home:certify", kwargs={"pk": stat.id}), data=data)

        self.assertIn(stat, EEPProgramHomeStatus.objects.filter_by_company(provider_user.company))

        self.assertEqual(response.status_code, 302)
        stat = EEPProgramHomeStatus.objects.get(id=stat.id)
        self.assertEqual(stat.certification_date, data["certification_date"])
        self.assertEqual(stat.state, "complete")

        # available relationship companies
        # (builder, rater, provider) must receive certification message
        self.assertEqual(send_message.call_count, 3)

    @mock.patch("axis.home.signals.HomeCertifiedMessage.send")
    def test_certify_customer_hirl_home(self, send_message):
        # customer hirl company and user
        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs",
            slug=customer_hirl_app.CUSTOMER_SLUG,
            is_eep_sponsor=True,
        )

        hirl_user = provider_user_factory(company=hirl_company)

        with self.subTest("Certify MF project"):
            mf_eep_program = basic_eep_program_factory(
                name="MF 2020 New Construction",
                slug="ngbs-mf-new-construction-2020-new",
                customer_hirl_certification_fee=300,
                customer_hirl_per_unit_fee=30,
                owner=hirl_company,
                is_multi_family=True,
            )

            developer_organization = developer_organization_factory()
            architect_organization = architect_organization_factory()
            communityowner_organization = communityowner_organization_factory()

            # builder with Counter-Signed builder agreement
            builder_organization = builder_organization_factory()
            builder_user = builder_user_factory(company=builder_organization)

            builder_agreement_factory(
                company=builder_organization,
                owner=hirl_company,
                state=BuilderAgreement.COUNTERSIGNED,
            )

            Relationship.objects.create_mutual_relationships(hirl_company, builder_organization)

            # Verifier
            rater_company = rater_organization_factory()
            rater_user = rater_user_factory(company=rater_company)
            Relationship.objects.create_mutual_relationships(hirl_company, rater_company)
            Relationship.objects.create_mutual_relationships(rater_company, builder_organization)

            # Registration and project
            mf_registration = hirl_project_registration_factory(
                eep_program=mf_eep_program,
                project_type=HIRLProjectRegistration.MULTI_FAMILY_PROJECT_TYPE,
                registration_user=rater_user,
                builder_organization=builder_organization,
                developer_organization=developer_organization,
                architect_organization=architect_organization,
                community_owner_organization=communityowner_organization,
            )
            mf_project = hirl_project_factory(
                street_line1="479 Washington St",
                registration=mf_registration,
                home_address_geocode_response=None,
                home_status=SET_NULL,
                story_count=1,
                number_of_units=1,
            )

            mf_registration.active()
            mf_project.save()

            mf_project.create_home_status()
            mf_project.save()

            # Pay all invoices
            invoice = invoice_factory()
            mf_project.home_status.invoiceitemgroup_set.update(invoice=invoice)

            mf_project.pay(amount=1000, paid_by=builder_user)
            mf_project.save()

            # Ready for certification
            self.assertEqual(mf_project.home_status.is_eligible_for_certification(), True)

            self.assertTrue(
                self.client.login(username=hirl_user.username, password="password"),
                msg="User %s [pk=%s] is not allowed to login" % (hirl_user.username, hirl_user.pk),
            )

            data = {"certification_date": datetime.date.today()}

            # pass QA
            qa_requirement_rough = QARequirement.objects.create(
                qa_company=hirl_company,
                type=QARequirement.ROUGH_INSPECTION_QA_REQUIREMENT_TYPE,
                eep_program=mf_eep_program,
            )

            qa_requirement_final = QARequirement.objects.create(
                qa_company=hirl_company,
                type=QARequirement.FINAL_INSPECTION_QA_REQUIREMENT_TYPE,
                eep_program=mf_eep_program,
            )

            QAStatus.objects.create(
                requirement=qa_requirement_rough,
                owner=rater_company,
                home_status=mf_project.home_status,
                result=QAStatus.PASS_STATUS,
            )

            QAStatus.objects.create(
                requirement=qa_requirement_final,
                owner=rater_company,
                home_status=mf_project.home_status,
                result=QAStatus.PASS_STATUS,
            )

            update_home_states(eepprogramhomestatus_id=mf_project.home_status.id)

            mf_project.refresh_from_db()

            response = self.client.post(
                reverse("home:certify", kwargs={"pk": mf_project.home_status.id}), data=data
            )
            self.assertIsNotNone(
                EEPProgramHomeStatus.objects.get(id=mf_project.home_status.id).certification_date
            )

            mf_project.refresh_from_db()
            self.assertEqual(
                mf_project.certification_counter,
                customer_hirl_app.LEGACY_PROJECT_CERTIFICATION_COUNTER + 1,
            )

            # available relationship companies
            # (builder, rater, provider, architect, developer, communityowner)
            #  must receive certification message
            self.assertEqual(send_message.call_count, 6)
            send_message.call_count = 0

        with self.subTest("Certify another SF project"):
            # Registration and project
            sf_eep_program = basic_eep_program_factory(
                name="MF 2020 New Construction",
                slug="ngbs-sf-new-construction-2020-new",
                customer_hirl_certification_fee=300,
                customer_hirl_per_unit_fee=30,
                owner=hirl_company,
                is_multi_family=False,
            )

            sf_registration = hirl_project_registration_factory(
                eep_program=sf_eep_program,
                project_type=HIRLProjectRegistration.SINGLE_FAMILY_PROJECT_TYPE,
                registration_user=rater_user,
                builder_organization=builder_organization,
            )
            sf_project = hirl_project_factory(
                street_line1="479 Washington St",
                registration=sf_registration,
                home_address_geocode_response=None,
                home_status=SET_NULL,
            )

            sf_registration.active()
            sf_registration.save()

            sf_project.create_home_status()
            sf_project.save()

            # Pay all invoices
            invoice = invoice_factory()
            sf_project.home_status.invoiceitemgroup_set.update(invoice=invoice)

            sf_project.pay(amount=1000, paid_by=builder_user)
            sf_project.save()

            # pass QA
            qa_requirement_rough = QARequirement.objects.create(
                qa_company=hirl_company,
                type=QARequirement.ROUGH_INSPECTION_QA_REQUIREMENT_TYPE,
                eep_program=sf_eep_program,
            )

            qa_requirement_final = QARequirement.objects.create(
                qa_company=hirl_company,
                type=QARequirement.FINAL_INSPECTION_QA_REQUIREMENT_TYPE,
                eep_program=sf_eep_program,
            )

            QAStatus.objects.create(
                requirement=qa_requirement_rough,
                owner=rater_company,
                home_status=sf_project.home_status,
                result=QAStatus.PASS_STATUS,
            )

            QAStatus.objects.create(
                requirement=qa_requirement_final,
                owner=rater_company,
                home_status=sf_project.home_status,
                result=QAStatus.PASS_STATUS,
            )

            update_home_states(eepprogramhomestatus_id=sf_project.home_status.id)

            sf_project.refresh_from_db()

            # Ready for certification
            self.assertEqual(sf_project.home_status.is_eligible_for_certification(), True)

            self.assertTrue(
                self.client.login(username=hirl_user.username, password="password"),
                msg="User %s [pk=%s] is not allowed to login" % (hirl_user.username, hirl_user.pk),
            )

            self.assertEqual(send_message.call_count, 0)
            data = {"certification_date": datetime.date.today()}
            self.client.post(
                reverse("home:certify", kwargs={"pk": sf_project.home_status.id}), data=data
            )
            status = EEPProgramHomeStatus.objects.get(id=sf_project.home_status.id)
            self.assertIsNotNone(status.certification_date)

            sf_project.refresh_from_db()
            self.assertEqual(
                sf_project.certification_counter,
                customer_hirl_app.LEGACY_PROJECT_CERTIFICATION_COUNTER + 2,
            )

            # available relationship companies
            # (builder, rater, provider, builder, architect, community)
            # should receive certification message - axis/home/signals.py:189
            self.assertEqual(len(set(status.home.relationships.values_list("company_id"))), 6)
            self.assertEqual(send_message.call_count, 6)

            send_message.call_count = 0

            with self.subTest("Certify SF project with WRI Program"):
                # Registration and project
                sf_eep_program = basic_eep_program_factory(
                    name="Some WRI Program",
                    slug=random.choice(customer_hirl_app.WRI_PROGRAM_LIST),
                    customer_hirl_certification_fee=50,
                    customer_hirl_per_unit_fee=30,
                    owner=hirl_company,
                    is_multi_family=False,
                )

                sf_registration = hirl_project_registration_factory(
                    eep_program=sf_eep_program,
                    project_type=HIRLProjectRegistration.SINGLE_FAMILY_PROJECT_TYPE,
                    registration_user=rater_user,
                    builder_organization=builder_organization,
                )
                sf_project = hirl_project_factory(
                    street_line1="479 Washington St",
                    registration=sf_registration,
                    home_address_geocode_response=None,
                    home_status=SET_NULL,
                )

                sf_registration.active()
                sf_registration.save()

                sf_project.create_home_status()
                sf_project.save()

                # Pay all invoices
                invoice = invoice_factory()
                sf_project.home_status.invoiceitemgroup_set.update(invoice=invoice)

                sf_project.pay(amount=1000, paid_by=builder_user)
                sf_project.save()

                # pass QA
                qa_requirement_rough = QARequirement.objects.create(
                    qa_company=hirl_company,
                    type=QARequirement.ROUGH_INSPECTION_QA_REQUIREMENT_TYPE,
                    eep_program=sf_eep_program,
                )

                qa_requirement_final = QARequirement.objects.create(
                    qa_company=hirl_company,
                    type=QARequirement.FINAL_INSPECTION_QA_REQUIREMENT_TYPE,
                    eep_program=sf_eep_program,
                )

                QAStatus.objects.create(
                    requirement=qa_requirement_rough,
                    owner=rater_company,
                    home_status=sf_project.home_status,
                    result=QAStatus.PASS_STATUS,
                )

                QAStatus.objects.create(
                    requirement=qa_requirement_final,
                    owner=rater_company,
                    home_status=sf_project.home_status,
                    result=QAStatus.PASS_STATUS,
                )

                update_home_states(eepprogramhomestatus_id=sf_project.home_status.id)

                sf_project.refresh_from_db()

                # Ready for certification
                self.assertEqual(sf_project.home_status.is_eligible_for_certification(), True)

                self.assertTrue(
                    self.client.login(username=hirl_user.username, password="password"),
                    msg="User %s [pk=%s] is not allowed to login"
                    % (hirl_user.username, hirl_user.pk),
                )

                data = {"certification_date": datetime.date.today()}

                response = self.client.post(
                    reverse("home:certify", kwargs={"pk": sf_project.home_status.id}), data=data
                )
                self.assertIsNotNone(
                    EEPProgramHomeStatus.objects.get(
                        id=sf_project.home_status.id
                    ).certification_date
                )

                sf_project.refresh_from_db()

                # check that certification_counter is not increased
                self.assertEqual(
                    sf_project.certification_counter,
                    0,
                )
                # check that wri_certification_counter is increased
                self.assertEqual(
                    sf_project.wri_certification_counter,
                    1,
                )
                # Companies must receive certification message
                self.assertEqual(send_message.call_count, 6)


class HomeExamineTests(HomeViewTestsMixins, ApiV3Tests):
    client_class = AxisClient

    maxDiff = None

    def test_examine_create_basic(self):
        """A home with a subdivision specified should become is_custom_home=False."""
        from axis.geographic.models import City
        from axis.subdivision.models import Subdivision

        user = self.get_admin_user(company_type="rater")
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        driver = MachineryDriver(HomeExamineMachinery, create_new=True, request_user=user)
        driver.set_ignore_fields(
            "id",
            "city_name",
            "state",
            "metro",
            "metro_name",
            "metro_display",
            "county",
            "address_designator",
            "county_name",
            "country_name",
            "latitude",
            "longitude",
            "subdivision_name",
            "subdivision_url",
            "confirmed_address",
            "raw_address",
            "geocoded_address",
            "subdivision_is_multi_family",
            "geocode_response_display",
            "lot_number_display",
            "street_line1_display",
            "city_display",
            "state_display",
            "zipcode_display",
            "climate_zone",
            "climate_zone_display",
            "confirmed_address_display",
            "latitude_display",
            "longitude_display",
        )

        subdivision = Subdivision.objects.filter_by_company(user.company)[0]
        data = {
            "lot_number": "1234567890",
            "street_line1": "694 W La Pryor Ln",
            "subdivision": subdivision.id,
            "zipcode": "85233",
            # Selecting a Subdivision on the frontend autopopulates the corresponding City
            "city": City.objects.get(name="Gilbert").id,
        }
        data["geocode_response"] = Geocode.objects.get_matches(**data)[0].id
        driver.bind(data)

        client_object = driver.get_client_object()

        response = driver.submit(self.client, method="post")
        response_object = driver.get_response_object()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(client_object, response_object)

        obj = Home.objects.get(lot_number=1234567890)
        self.assertEqual(obj.is_custom_home, False)

    def test_examine_intl_create(self):
        city = real_city_factory("Bonao", country="DO")

        user = self.admin_user
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        driver = MachineryDriver(HomeExamineMachinery, create_new=True, request_user=user)
        driver.bind(
            dict(
                lot_number="1234567890",
                street_line1="WHFW+4P3",
                street_line2="",
                city=city.pk,
                zipcode="85233",
            ),
        )

        response = driver.submit(self.client, method="post")
        response_object = driver.get_response_object()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Home.objects.filter(id=response_object["id"]).exists(), True)

    def test_examine_create_custom(self):
        """A home without a subdivision specified should become is_custom_home=True."""
        from axis.geographic.models import City

        user = self.get_admin_user(company_type="rater")
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        driver = MachineryDriver(HomeExamineMachinery, create_new=True, request_user=user)
        driver.set_ignore_fields(
            "id",
            "city_name",
            "state",
            "metro",
            "metro_name",
            "metro_display",
            "county",
            "address_designator",
            "county_name",
            "country_name",
            "latitude",
            "longitude",
            "subdivision_name",
            "subdivision_url",
            "confirmed_address",
            "raw_address",
            "geocoded_address",
            "geocode_response_display",
            "lot_number_display",
            "street_line1_display",
            "city_display",
            "state_display",
            "zipcode_display",
            "climate_zone",
            "climate_zone_display",
            "confirmed_address_display",
            "latitude_display",
            "longitude_display",
        )

        data = {
            "lot_number": "1234567890",
            "street_line1": "694 W La Pryor Ln",
            "subdivision": None,
            "zipcode": "85233",
            # City is required, no subdivision to auto-fill it
            "city": City.objects.get(name="Gilbert").id,
        }
        data["geocode_response"] = Geocode.objects.get_matches(**data)[0].id
        driver.bind(data)

        client_object = driver.get_client_object()

        response = driver.submit(self.client, method="post")
        response_object = driver.get_response_object()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(client_object, response_object)

        obj = Home.objects.get(lot_number=1234567890)
        self.assertEqual(obj.is_custom_home, True)

    def test_examine_update(self):
        """Tests that the update process updates relationships to companies."""
        user = self.get_admin_user(company_type="rater")
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        instance = Home.objects.filter_by_user(user)[0]
        driver = MachineryDriver(HomeExamineMachinery, instance=instance, request_user=user)
        driver.set_ignore_fields(
            "id",
            "city_name",
            "metro",
            "county",
            "street_line1_display",
            "city_display",
            "state_display",
            "zipcode_display",
            "lot_number_display",
        )

        data = {
            "lot_number": "something new",
        }

        driver.bind(data)

        client_object = driver.get_client_object()

        response = driver.submit(self.client, method="patch")
        response_object = driver.get_response_object()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(client_object["lot_number"], response_object["lot_number"])
        self.assertEqual(client_object, response_object)

    def test_examine_update_becomes_custom(self):
        """Tests that the update process can convert a home to custom."""
        from axis.geographic.models import City
        from axis.subdivision.models import Subdivision

        user = self.get_admin_user(company_type="rater")
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        instance = Home.objects.create(
            **{
                "street_line1": "nowhere ln",
                "street_line2": "",
                "city": City.objects.all()[0],
                "zipcode": "54829",
                "subdivision": Subdivision.objects.all()[0],
                "is_custom_home": False,
            }
        )
        driver = MachineryDriver(HomeExamineMachinery, instance=instance, request_user=user)
        driver.set_ignore_fields(
            "id",
            "city_name",
            "metro",
            "county",
            "street_line1_display",
            "city_display",
            "state_display",
        )
        data = {
            "subdivision": None,
        }
        driver.bind(data)

        client_object = driver.get_client_object()

        response = driver.submit(self.client, method="patch")
        response_object = driver.get_response_object()
        self.assertEqual(response.status_code, 200)

        # Re-fetch object so values are fresh
        instance = Home.objects.get(pk=instance.pk)
        self.assertEqual(instance.is_custom_home, True)

    def test_examine_update_becomes_non_custom(self):
        from axis.geographic.models import City
        from axis.subdivision.models import Subdivision

        user = self.get_admin_user(company_type="rater")
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        instance = Home.objects.create(
            **{
                "street_line1": "nowhere ln",
                "street_line2": "",
                "city": City.objects.all()[0],
                "zipcode": "54829",
                "subdivision": None,
                "is_custom_home": True,
            }
        )
        driver = MachineryDriver(HomeExamineMachinery, instance=instance, request_user=user)
        driver.set_ignore_fields(
            "id",
            "city_name",
            "metro",
            "county",
            "street_line1_display",
            "city_display",
            "state_display",
        )
        data = {
            "subdivision": Subdivision.objects.all()[0].id,
        }
        driver.bind(data)

        client_object = driver.get_client_object()

        response = driver.submit(self.client, method="patch")
        response_object = driver.get_response_object()
        self.assertEqual(response.status_code, 200)

        # Re-fetch object so values are fresh
        instance = Home.objects.get(pk=instance.pk)
        self.assertEqual(instance.is_custom_home, False)

    def test_examine_create_relationships(self):
        from axis.core.views.machinery import object_relationships_machinery_factory

        user = self.get_admin_user(company_type="rater")
        other_company_user = user.company.users.exclude(id=user.id).first()

        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        instance = Home.objects.filter_by_user(user)[0]
        # Drop all existing relationships
        instance.relationships.all().delete()

        machinery_class = object_relationships_machinery_factory(Home)
        driver = MachineryDriver(machinery_class, instance=instance, request_user=user)
        client_object = driver.get_client_object()
        self.assertEqual(not (client_object.get("urls")), True)

        # Add a relationship to prove out the list
        general = Company.objects.filter(company_type="general").first()
        self.assertIsNotNone(general)
        Relationship.objects.create_mutual_relationships(user.company, general)
        user.refresh_from_db()

        # Add companies
        companies = user.company.relationships.get_companies()
        builder = companies.filter(company_type="builder")[0]
        hvacs = companies.filter(company_type="hvac", is_customer=False).values_list(
            "id", flat=True
        )
        self.assertEqual(list(hvacs), [])  # We don't have any.
        general = companies.filter(company_type="general").values_list("id", flat=True)
        self.assertNotEqual(list(general), [])

        utility = companies.filter(company_type="utility")[0]
        eep = companies.filter(company_type="eep")[0]

        Message.objects.all().delete()

        data = {
            "eep": [eep.id],
            "builder": builder.id,
            "hvac": list(hvacs),
            "general": list(general),
            "gas_utility": utility.id,
        }
        driver.bind(data)
        driver.set_ignore_fields("names", "rater", "urls")

        client_object = driver.get_client_object()

        response = driver.submit(self.client, method="patch")
        response_object = driver.get_response_object()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(client_object, response_object)
        self.assertEqual(builder, instance.relationships.get_builder_orgs()[0])
        self.assertEqual(eep, instance.relationships.filter(company__company_type="eep")[0].company)
        self.assertEqual(utility.id, instance.get_gas_company().pk)
        self.assertEqual(set(general), set(instance.relationships.get_general_orgs(ids_only=True)))

        # Note there aren't any..
        self.assertEqual(set(hvacs), set(instance.relationships.get_hvac_orgs(ids_only=True)))
        # Verify we got no messages for our user.company
        self.assertEqual(Message.objects.filter(user=user).count(), 0)
        # Verify that these companies got messages.
        # Couple notes:  Messages are created regardless of the preferences.  Whether they
        # are send it another matter altogether.
        users_who_em = User.objects.filter(
            company_id__in=[eep.id, builder.id, utility.id, general[0]]
        )
        self.assertGreater(users_who_em.count(), 0)
        self.assertEqual(
            Message.objects.filter(user__in=users_who_em).count(), users_who_em.count()
        )

    def test_examine_update_relationships(self):
        from axis.core.views.machinery import object_relationships_machinery_factory

        user = self.get_admin_user(company_type="rater")
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        instance = Home.objects.filter_by_user(user)[0]
        machinery_class = object_relationships_machinery_factory(Home)
        driver = MachineryDriver(machinery_class, instance=instance, request_user=user)

        old_builders = list(instance.relationships.get_builder_orgs(ids_only=True))
        old_hvacs = list(instance.relationships.get_hvac_orgs(ids_only=True))
        old_general = list(instance.relationships.get_general_orgs(ids_only=True))
        old_utilities = list(instance.relationships.get_utility_orgs(ids_only=True))

        companies = user.company.relationships.get_companies()
        builder = companies.filter(company_type="builder")[0]
        hvacs = companies.filter(company_type="hvac", is_customer=False).values_list(
            "id", flat=True
        )
        general = companies.filter(company_type="general", is_active=True).values_list(
            "id", flat=True
        )
        utility = companies.filter(company_type="utility")[0]
        data = {
            "builder": builder.id,
            "hvac": list(hvacs),
            "general": list(general),
            "gas_utility": utility.id,
        }
        driver.bind(data)

        client_object = driver.get_client_object()

        response = driver.submit(self.client, method="patch")
        response_object = driver.get_response_object()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(client_object, response_object)
        self.assertEqual(
            builder.id, list(instance.relationships.get_builder_orgs(ids_only=True))[0]
        )
        self.assertEqual(set(hvacs), set(instance.relationships.get_hvac_orgs(ids_only=True)))
        self.assertEqual(
            set(old_general + list(general)),
            set(instance.relationships.get_general_orgs(ids_only=True)),
        )
        self.assertEqual(utility.id, instance.get_gas_company().pk)

        instance = Home.objects.get(id=instance.id)

        new_builder = Company.objects.create(
            name="brand new", company_type=Company.BUILDER_COMPANY_TYPE
        )
        user.company.relationships.create(company=new_builder, content_object=user.company)
        data = {
            "builder": new_builder.id,
        }
        driver.bind(data)
        response = driver.submit(self.client, method="patch")
        self.assertEqual(response.status_code, 200)
        instance = Home.objects.get(id=instance.id)
        self.assertEqual(new_builder, instance.relationships.get_builder_orgs()[0])

    def test_examine_update_relationships_propagate_to_floorplan_when_mutual_relationship_with_owner(
        self,
    ):
        """
        Given an already set up EEPProgramHomeStatus
        When a company relationship is added to the Home
        And the Company being added has a mutual relationship with the EEPProgramHomeStatus owner
        Then the EEPProgramHomeStatus floorplan should get a direct relationship with the new company
        """
        from axis.core.views.machinery import object_relationships_machinery_factory

        user = self.get_admin_user(company_type="rater")
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        # Get home and unattached company
        home_stat = EEPProgramHomeStatus.objects.first()
        unrelated_provider = Company.objects.get(name="unrelated_provider")
        unrelated_rater = Company.objects.get(name="unrelated_rater")

        # Ensure HomeStat Company is not the Floorplan owner
        home_stat.floorplan.owner = unrelated_rater
        home_stat.floorplan.save()

        # Create mutual relationship
        Relationship.objects.create_mutual_relationships(
            home_stat.floorplan.owner, unrelated_provider
        )

        # Examine wizardry
        machinery_class = object_relationships_machinery_factory(Home)
        driver = MachineryDriver(machinery_class, instance=home_stat.home, request_user=user)

        data = {"provider": [unrelated_provider.id]}
        driver.bind(data)
        driver.submit(self.client, method="patch")

        # Refresh the floorplan to make sure we have the updated relationships
        floorplan = Floorplan.objects.get(id=home_stat.floorplan.id)
        relationships = floorplan.relationships.filter_by_company_type(
            unrelated_provider.company_type
        )
        self.assertIn(unrelated_provider.id, relationships.values_list("company__id", flat=True))

    def test_examine_update_relationships_do_not_propagate_to_floorplan_when_no_mutual_relationship_with_owner(
        self,
    ):
        """
        Given an already set up EEPProgramHomeStatus
        When a company relationship is added to a Home
        and the Company being added does not have a mutual relationship with the EEPProgramHomeStatus owner
        Then the EEPProgramHomeStatus floorplan should not get a relationship with the new company
        """
        from axis.core.views.machinery import object_relationships_machinery_factory

        user = self.get_admin_user(company_type="rater")
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        home_stat = EEPProgramHomeStatus.objects.first()
        unrelated_provider = Company.objects.get(name="unrelated_provider")
        unrelated_rater = Company.objects.get(name="unrelated_rater")

        # Ensure HomeStat Company is not the Floorplan owner
        home_stat.floorplan.owner = unrelated_rater
        home_stat.floorplan.save()

        machinery_class = object_relationships_machinery_factory(Home)
        driver = MachineryDriver(machinery_class, instance=home_stat.home, request_user=user)

        data = {"provider": [unrelated_provider.id]}
        driver.bind(data)
        driver.submit(self.client, method="patch")

        floorplan = Floorplan.objects.get(id=home_stat.floorplan.id)
        relationships = floorplan.relationships.filter_by_company_type(
            unrelated_provider.company_type
        )
        self.assertNotIn(unrelated_provider.id, relationships.values_list("company__id", flat=True))

    def test_homedocument_ajax_upload_create(self):
        """Tests that documents can be posted to the home."""
        user = self.get_admin_user(company_type="rater")
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        instance = Home.objects.filter_by_company(user.company)[1]

        M = customerdocument_machinery_factory(Home)
        driver = MachineryDriver(M, create_new=True, request_user=user)
        data = {
            "object_id": instance.id,
            "document_raw": driver.encode_file(__file__),
            "document_raw_name": "__file__",
            "description": "Description",
            "is_public": True,
        }
        driver.bind(data)

        client_object = driver.get_client_object()

        response = driver.submit(self.client, method="post")
        response_object = driver.get_response_object()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(CustomerDocument.objects.filter(id=response_object["id"]).exists(), True)
        self.assertEqual(bool(response_object["document"]), True)  # path will be sort of random

    def test_homedocument_ajax_upload_update(self):
        """Tests that documents can be updated."""
        user = self.get_admin_user(company_type="rater")
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        self.test_homedocument_ajax_upload_create()

        instance = Home.objects.filter_by_company(user.company)[1]
        document = instance.customer_documents.all()[0]

        M = customerdocument_machinery_factory(Home)
        driver = MachineryDriver(M, instance=document, request_user=user)
        data = {
            "object_id": instance.id,
            "document_raw": driver.encode_file(__file__),
            "document_raw_name": "__file__",
            "description": "Ma Rose, ma chere",
            "is_public": True,
        }
        driver.bind(data)

        client_object = driver.get_client_object()

        response = driver.submit(self.client, method="patch")
        response_object = driver.get_response_object()
        self.assertEqual(response.status_code, 200)

    def test_examine_geocoding(self):
        """Test the geo-coding side of a home.."""

        self.test_examine_create_basic()

        home = Home.objects.get(lot_number="1234567890")

        self.assertEqual(home.confirmed_address, True)
        self.assertIsNotNone(home.latitude)
        self.assertIsNotNone(home.longitude)

        # Turn this into a bad address again:
        home.geocode_response = None
        home.confirmed_address = False
        home.latitude = None
        home.longitude = None
        home.save()

        # Verify our temp changes stuck..
        self.assertEqual(home.confirmed_address, False)
        self.assertIsNone(home.latitude)
        self.assertIsNone(home.longitude)


class ActiveFloorplanExamineTests(HomeViewTestsMixins, ApiV3Tests):
    def test_active_floorplan_machinery_for_os_eri(self):
        user_obj = self.get_admin_user(company_type="rater")
        self.assertTrue(
            self.client.login(username=user_obj.username, password="password"),
            msg=f"User {user_obj.username} [pk={user_obj.pk}] is not allowed to login",
        )

        instance = EEPProgramHomeStatus.objects.filter_by_company(user_obj.company).first()
        floorplan = instance.floorplan
        self.assertIsNotNone(instance.floorplan)

        driver = MachineryDriver(
            ActiveFloorplanExamineMachinery,
            instance=floorplan,
            request_user=user_obj,
            context={"home_status_id": instance.pk},
        )
        client_object = driver.get_client_object()
        self.assertIsNotNone(client_object["owner"])
        self.assertIsNone(client_object["remrate_target"])
        self.assertIsNone(client_object["simulation"])

        class MockRequest:
            user = user_obj

        with self.subTest("Missing simulation - No OS ERI Available"):
            machinery = ActiveFloorplanExamineMachinery(
                instance=floorplan,
                context={"home_status_id": instance.pk, "request": MockRequest},
            )
            data = machinery.get_helpers(floorplan)
            # print(json.dumps(data, indent=4))
            # dump_test_data(data)

            self.assertEqual(data["verbose_name"], "Floorplan")
            self.assertIsNotNone(data["home_status_id"])
            self.assertIsNone(data["open_studio_eri_data"])

            actions = machinery.get_default_actions(floorplan)
            self.assertEqual(len(actions), 0)
            # print(json.dumps(data, indent=4))
            # dump_test_data(data)

        with self.subTest("Valid simulation - OS ERI Available"):
            simulation = simulation_factory(skip_analysis=True, company=floorplan.owner)
            floorplan.simulation = simulation
            floorplan.save()

            machinery = ActiveFloorplanExamineMachinery(
                instance=floorplan,
                context={"home_status_id": instance.pk, "request": MockRequest},
            )
            data = machinery.get_helpers(floorplan)
            # print(json.dumps(data, indent=4))
            # dump_test_data(data)

            self.assertEqual(data["verbose_name"], "Floorplan")
            self.assertEqual(data["can_download_xml"], False)
            self.assertIsNotNone(data["home_status_id"])
            self.assertEqual(data["show_ceiling_r_values"], False)
            self.assertIsNotNone(data["hes_score_data"])
            self.assertIsNotNone(data["open_studio_eri_data"])
            self.assertIn("generate_url", data["open_studio_eri_data"])
            self.assertEqual(data["show_simulation_specifics"], False)

            # We should only have one action here - Simulate HES / Super only can get the OSERI
            actions = machinery.get_default_actions(floorplan)
            self.assertEqual(len(actions), 1)
            self.assertEqual(actions[0]["instruction"], "simulateHES")

        with self.subTest("Valid simulation - OS ERI Available Menu Pick"):
            user_obj.is_superuser = True
            user_obj.save()
            machinery = ActiveFloorplanExamineMachinery(
                instance=floorplan,
                context={"home_status_id": instance.pk, "request": MockRequest},
            )
            actions = machinery.get_default_actions(floorplan)
            self.assertEqual(len(actions), 2)
            # print(json.dumps(data, indent=4))
            # dump_test_data(actions[1])
            self.assertEqual(actions[1]["name"], "Get OpenStudio-ERI Score")
            self.assertEqual(actions[1]["instruction"], "simulateOpenStudio")

        with self.subTest("Valid OS-ERI Simulation started"):
            analysis = analysis_factory(
                engine=AnalysisEngine.EPLUS,
                type=AnalysisType.OS_ERI_2014AEG_DESIGN,
                simulation=simulation,
                status=AnalysisStatus.STARTED,
            )
            machinery = ActiveFloorplanExamineMachinery(
                instance=floorplan,
                context={"home_status_id": instance.pk, "request": MockRequest},
            )
            actions = machinery.get_default_actions(floorplan)
            self.assertEqual(len(actions), 2)
            # print(json.dumps(data, indent=4))
            # dump_test_data(actions[1])
            self.assertEqual(actions[1]["name"], "OpenStudio-ERI: score Started...")
            self.assertEqual(actions[1]["instruction"], "none")

        with self.subTest("Valid OS-ERI Simulation failed"):
            analysis.status = AnalysisStatus.FAILED
            analysis.save()
            machinery = ActiveFloorplanExamineMachinery(
                instance=floorplan,
                context={"home_status_id": instance.pk, "request": MockRequest},
            )
            actions = machinery.get_default_actions(floorplan)
            self.assertEqual(len(actions), 2)
            # print(json.dumps(data, indent=4))
            # dump_test_data(actions[1])
            self.assertEqual(actions[1]["name"], "OpenStudio-ERI: ERROR (click to re-run)")
            self.assertEqual(actions[1]["instruction"], "simulateOpenStudio")

        with self.subTest("Valid OS-ERI Simulation Complete"):
            analysis.status = AnalysisStatus.COMPLETE
            analysis.save()
            machinery = ActiveFloorplanExamineMachinery(
                instance=floorplan,
                context={"home_status_id": instance.pk, "request": MockRequest},
            )
            actions = machinery.get_default_actions(floorplan)
            self.assertEqual(len(actions), 2)
            # print(json.dumps(data, indent=4))
            # dump_test_data(actions[1])
            self.assertEqual(actions[1]["name"], "Regenerate OpenStudio-ERI score")
            self.assertEqual(actions[1]["instruction"], "simulateOpenStudio")


class HomeStatusReportFilterTests(HostStatusReportMixin, AxisTestCase):
    client_class = AxisClient

    def setUp(self):
        self.user = self.user_model.objects.get(username="tester")
        self.queryset = EEPProgramHomeStatus.objects.filter_by_user(self.user)
        self.view = HomeStatusReportMixin()
        self.filter = partial(self.view.get_external_qs_filters, self.queryset, self.user)

    def test_filter_by_subdivision(self):
        from axis.subdivision.models import Subdivision

        sub = Subdivision.objects.all()[1]

        kwargs = {"subdivision_id": sub.id}
        home_stats = self.filter(**kwargs)
        self.assertGreater(home_stats.count(), 0)

        for stat in home_stats:
            self.assertEqual(stat.home.subdivision, sub)

    def test_filter_by_eep_program(self):
        from axis.eep_program.models import EEPProgram

        eep = EEPProgram.objects.all()[1]

        kwargs = {"eep_program_id": eep.id}
        home_stats = self.filter(**kwargs)
        self.assertGreater(home_stats.count(), 0)

        for stat in home_stats:
            self.assertEqual(stat.eep_program, eep)

    def test_filter_by_builder(self):
        from axis.company.models import Company

        builder = Company.objects.get(name="Test Builder")

        kwargs = {"builder_id": builder.id}
        home_stats = self.filter(**kwargs)
        self.assertGreater(home_stats.count(), 0)

        for stat in home_stats:
            self.assertEqual(stat.home.get_builder(), builder)

    def test_filter_by_company_type(self):
        """Pick one company type to test."""
        kwargs = {"rater_id": self.user.company.id}
        home_stats = self.filter(**kwargs)
        self.assertGreater(home_stats.count(), 0)

        for stat in home_stats:
            for rel in stat.home.relationships.filter(company__company_type="rater"):
                self.assertEqual(rel.company, self.user.company)

    def test_filter_by_location_us_state(self):
        state = Home.objects.all().values_list("state", flat=True)[1]

        kwargs = {"us_state": state}
        home_stats = self.filter(**kwargs)
        self.assertGreater(home_stats.count(), 0)

        for stat in home_stats:
            self.assertEqual(stat.home.state, state)

    def test_filter_by_location_metro(self):
        metro = Home.objects.all().values_list("metro_id", flat=True)[1]

        kwargs = {"metro_id": metro}
        home_stats = self.filter(**kwargs)
        self.assertGreater(home_stats.count(), 0)

        for stat in home_stats:
            self.assertEqual(stat.home.metro_id, metro)

    def test_filter_by_location_us_state_and_metro(self):
        state, metro = Home.objects.all().values_list("state", "metro_id")[1]

        kwargs = {"us_state": state, "metro_id": metro}
        home_stats = self.filter(**kwargs)
        self.assertGreater(home_stats.count(), 0)

        for stat in home_stats:
            self.assertEqual(stat.home.state, state)
            self.assertEqual(stat.home.metro_id, metro)

    def test_filter_by_location_bad_state(self):
        """Make sure no homes are returned if we try to filter by a US state that does not exist."""
        state = "BZ"
        kwargs = {"us_state": state}
        home_stats = self.filter(**kwargs)
        self.assertEqual(home_stats.count(), 0)

    def test_filter_by_certification(self):
        activity_stop = EEPProgramHomeStatus.objects.filter(
            certification_date__isnull=False
        ).values_list("certification_date", flat=True)[1]
        activity_start = activity_stop - datetime.timedelta(days=1)

        kwargs = {
            "certification_only": True,
            "activity_start": activity_start,
            "activity_stop": activity_stop,
        }
        home_stats = self.filter(**kwargs)
        self.assertGreater(home_stats.count(), 0)

        all_certified = EEPProgramHomeStatus.objects.filter(certification_date__isnull=False)
        self.assertNotEqual(home_stats.count(), all_certified.count())

        for stat in home_stats:
            self.assertIsNotNone(stat.certification_date)
            self.assertGreaterEqual(stat.certification_date, activity_start)
            self.assertLessEqual(stat.certification_date, activity_stop)

    def test_filter_by_state_not_certified(self):
        state = "-1"
        kwargs = {"state": state}
        home_stats = self.filter(**kwargs)
        self.assertGreater(home_stats.count(), 0)

        for stat in home_stats:
            self.assertNotEqual(stat.state, "complete")

    def test_filter_by_state_pending_inspection(self):
        state = "pending_inspection"
        activity_stop = (
            EEPProgramHomeStatus.objects.all()
            .order_by("-created_date")
            .values_list("created_date", flat=True)[1]
        )
        activity_start = activity_stop - datetime.timedelta(days=1)

        kwargs = {"state": state, "activity_start": activity_start, "activity_stop": activity_stop}
        home_stats = self.filter(**kwargs)
        self.assertGreater(home_stats.count(), 0)

        for stat in home_stats:
            self.assertEqual(stat.state, state)
            self.assertGreaterEqual(stat.created_date, activity_start)
            self.assertLessEqual(stat.created_date, activity_stop)

    def test_filter_by_state(self):
        state = "complete"
        home_stats = self.filter(state=state)
        self.assertGreater(home_stats.count(), 0)

        for stat in home_stats:
            self.assertEqual(stat.state, state)

    def test_filter_by_state_with_dates(self):
        activity_stop = EEPProgramHomeStatus.objects.filter_by_user(self.user).values_list(
            "state_history__start_time", flat=True
        )[1]
        activity_start = activity_stop - datetime.timedelta(days=1)

        state = "qa_pending"
        kwargs = {"state": state, "activity_start": activity_start, "activity_stop": activity_stop}
        home_stats = self.filter(**kwargs)
        self.assertGreater(home_stats.count(), 0)

        for stat in home_stats:
            history = stat.state_history.filter(to_state=state)
            self.assertGreater(history.count(), 0)
            for step in history:
                self.assertGreaterEqual(step.start_time.date(), activity_start.date())
                self.assertLessEqual(step.start_time.date(), activity_stop.date())

    def test_filter_by_ipp_state_not_received(self):
        from axis.incentive_payment.models import IncentivePaymentStatus

        state = "-2"
        kwargs = {"ipp_state": state}
        home_stats = self.filter(**kwargs)
        self.assertGreater(home_stats.count(), 0)

        for stat in home_stats:
            with self.assertRaises(IncentivePaymentStatus.DoesNotExist):
                stat.incentivepaymentstatus

    def test_filter_by_ipp_state_not_paid(self):
        state = "-1"
        kwargs = {
            "ipp_state": state,
        }
        home_stats = self.filter(**kwargs)
        self.assertGreater(home_stats.count(), 0)

        for stat in home_stats:
            self.assertNotEqual(stat.incentivepaymentstatus.state, "complete")

    def test_filter_by_ipp_state(self):
        state = "complete"
        home_stats = self.filter(state=state)
        self.assertGreater(home_stats.count(), 0)

        for stat in home_stats:
            self.assertEqual(stat.state, state)

    def test_filter_by_ipp_state_with_dates(self):
        activity_stop = max(
            EEPProgramHomeStatus.objects.filter_by_user(
                self.user, incentivepaymentstatus__state_history__isnull=False
            ).values_list("incentivepaymentstatus__state_history__start_time", flat=True)
        )

        activity_start = activity_stop - datetime.timedelta(days=1)

        state = "ipp_payment_requirements"
        kwargs = {
            "ipp_state": state,
            "activity_start": activity_start,
            "activity_stop": activity_stop,
        }
        home_stats = self.filter(**kwargs)
        self.assertGreater(home_stats.count(), 0)

        for stat in home_stats:
            history = stat.incentivepaymentstatus.state_history.filter(to_state=state)
            self.assertGreater(history.count(), 0)
            for step in history:
                self.assertGreaterEqual(step.start_time.date(), activity_start.date())
                self.assertLessEqual(step.start_time.date(), activity_stop.date())

    def test_filter_by_qa_status_does_not_exist(self):
        state = "-2"
        kwargs = {"qastatus": state}
        home_stats = self.filter(**kwargs)
        self.assertGreater(home_stats.count(), 0)

        for stat in home_stats:
            self.assertEqual(stat.qastatus_set.count(), 0)

    def test_filter_by_qa_status_not_complete(self):
        state = "-1"
        kwargs = {"qastatus": state}
        home_stats = self.filter(**kwargs)
        self.assertGreater(home_stats.count(), 0)

        for stat in home_stats:
            for qastatus in stat.qastatus_set.all():
                self.assertNotEqual(qastatus.state, "complete")

    def test_filter_by_qa_status(self):
        from axis.qa.models import QAStatus

        states = dict(QAStatus.get_state_choices())

        state = list(states.keys())[1]
        kwargs = {"qastatus": state}
        home_stats = self.filter(**kwargs)
        self.assertGreater(home_stats.count(), 0)

        for stat in home_stats:
            for qa_stat in stat.qastatus_set.all():
                self.assertEqual(qa_stat.state, state)

    def test_filter_by_qa_status_with_dates(self):
        from axis.qa.models import QAStatus

        states = dict(QAStatus.get_state_choices())

        activity_stop = EEPProgramHomeStatus.objects.filter_by_user(
            self.user, qastatus__isnull=False
        ).values_list("qastatus__state_history__start_time", flat=True)[1]
        activity_start = activity_stop - datetime.timedelta(days=1)

        state = list(states.keys())[1]
        kwargs = {
            "qastatus": state,
            "activity_start": activity_start,
            "activity_stop": activity_stop,
        }
        home_stats = self.filter(**kwargs)
        self.assertGreater(home_stats.count(), 0)

        for stat in home_stats:
            for qa_stat in stat.qastatus_set.all():
                history = qa_stat.state_history.filter(to_state=state)
                self.assertGreater(history.count(), 0)
                for step in history:
                    self.assertGreaterEqual(step.start_time.date(), activity_start.date())
                    self.assertLessEqual(step.start_time.date(), activity_stop.date())


class HomeViewCertificationTests(CertificationTestMixin, AxisTestCase):
    """Test out homes app"""

    client_class = AxisClient

    def _get_admin_user_from_company(self, company):
        return self.user_model.objects.filter(is_company_admin=True, company=company).first()

    def test_provider_passing_self_certification(self):
        """This should aways pass it's not an issue"""
        stat = EEPProgramHomeStatus.objects.get(home__street_line1__iexact="1 should pass")

        user = self._get_admin_user_from_company(stat.company)
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        self.assertEqual(stat.state, "certification_pending")
        data = {"certification_date": datetime.date.today()}
        response = self.client.post(reverse("home:certify", kwargs={"pk": stat.id}), data=data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("home:view", kwargs={"pk": stat.home.id}))

        stat = EEPProgramHomeStatus.objects.get(id=stat.id)
        self.assertEqual(stat.certification_date, data.get("certification_date"))
        self.assertEqual(stat.state, "complete")

        # Do it again and verify we get an error
        response = self.client.post(reverse("home:certify", kwargs={"pk": stat.id}), data=data)
        self.assertEqual(response.status_code, 404)

    def test_provider_failing_answers_requirements(self):
        # Remove an answer it's no longer eligible
        from axis.checklist.models import Answer

        stat = EEPProgramHomeStatus.objects.get(home__street_line1__iexact="1 should pass")
        Answer.objects.filter(home=stat.home)[0].delete()
        stat.update_stats()

        self.assertEqual(stat.report_eligibility_for_certification(), ["1 unanswered question"])

        user = self._get_admin_user_from_company(stat.company)
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        data = {"certification_date": datetime.date.today()}
        response = self.client.post(reverse("home:certify", kwargs={"pk": stat.id}), data=data)
        self.assertEqual(response.status_code, 200)

        msg = strings.NOT_ELIGIBLE_FOR_CERTIFICATION.format(
            url=stat.home.get_absolute_url(), home=stat.home, program=stat.eep_program
        )
        # After Django 4.1 use this one
        # self.assertFormError(response.context["form"], field=None, errors=msg)
        self.assertFormError(response, "form", field=None, errors=msg)

        self.assertEqual(stat.state, "certification_pending")
        self.assertIsNone(stat.certification_date)

    def test_provider_failing_relationship_requirements(self):
        # Remove an answer it's no longer eligible
        stat = EEPProgramHomeStatus.objects.get(home__street_line1__iexact="1 should pass")

        self.assertEqual(stat.state, "certification_pending")
        self.assertEqual(stat.is_eligible_for_certification(), True)

        # Add in the list of requirements..
        stat.eep_program.require_hvac_assigned_to_home = True
        stat.eep_program.require_utility_assigned_to_home = True
        stat.eep_program.require_rater_assigned_to_home = True
        stat.eep_program.require_qa_assigned_to_home = True
        stat.eep_program.save()

        stat = EEPProgramHomeStatus.objects.get(id=stat.id)
        self.assertEqual(stat.state, "certification_pending")
        self.assertEqual(stat.is_eligible_for_certification(), False)

        errors = [
            strings.MISSING_QA.format(program=stat.eep_program),
            strings.MISSING_HVAC.format(program=stat.eep_program),
            strings.MISSING_RATER.format(program=stat.eep_program),
            strings.MISSING_UTILITY.format(program=stat.eep_program),
        ]

        issues = stat.report_eligibility_for_certification()
        self.assertEqual(set(errors), set(issues))

        user = self._get_admin_user_from_company(stat.company)
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        data = {"certification_date": datetime.date.today()}
        response = self.client.post(reverse("home:certify", kwargs={"pk": stat.id}), data=data)
        self.assertEqual(response.status_code, 200)

        msg = strings.NOT_ELIGIBLE_FOR_CERTIFICATION.format(
            url=stat.home.get_absolute_url(), home=stat.home, program=stat.eep_program
        )
        # After Django 4.1 use this one
        # self.assertFormError(response.context["form"], field=None, errors=msg)
        self.assertFormError(response, "form", field=None, errors=msg)

        self.assertEqual(stat.state, "certification_pending")
        self.assertIsNone(stat.certification_date)

    def test_rater_self_certification(self):
        """This verifies that a rater cannot certify homes"""
        user = self.get_admin_user(company_type="rater")
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        # Assign the rater to this otherwise good entry..
        stat = EEPProgramHomeStatus.objects.get(home__street_line1__iexact="1 rater_not pass")
        self.assertEqual(stat.state, "certification_pending")

        data = {"certification_date": datetime.date.today()}
        response = self.client.post(reverse("home:certify", kwargs={"pk": stat.id}), data=data)
        self.assertEqual(response.status_code, 200)

        msg = strings.FAILED_CERTIFICATION_NOT_ALLOWED_TO_CERTIFY.format(
            url=stat.home.get_absolute_url(), home=stat.home, program=stat.eep_program
        )
        # After Django 4.1 use this one
        # self.assertFormError(response.context["form"], field=None, errors=msg)
        self.assertFormError(response, "form", field=None, errors=msg)

        self.assertEqual(stat.state, "certification_pending")
        self.assertIsNone(stat.certification_date)

        # Provider should be able to certify this.
        user = self._get_admin_user_from_company(stat.get_provider())
        self.assertEqual(self.client.login(username=user.username, password="password"), True)
        response = self.client.post(reverse("home:certify", kwargs={"pk": stat.id}), data=data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("home:view", kwargs={"pk": stat.home.id}))

        stat = EEPProgramHomeStatus.objects.get(id=stat.id)
        self.assertEqual(stat.certification_date, data.get("certification_date"))
        self.assertEqual(stat.state, "complete")

    def test_sampleset_rater_self_certification(self):
        """This verifies that a rater cannot certify homes"""
        user = self.get_admin_user(company_type="rater")
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        # Assign the rater to this otherwise good entry..
        sampleset = SampleSet.objects.get(alt_name="passing ss")
        test_home = sampleset.samplesethomestatus_set.current().filter(is_test_home=True)[0]
        stat = EEPProgramHomeStatus.objects.get(id=test_home.home_status.id)
        self.assertEqual(stat.state, "certification_pending")

        data = {"certification_date": datetime.date.today()}
        response = self.client.post(reverse("home:certify", kwargs={"pk": stat.id}), data=data)
        self.assertEqual(response.status_code, 200)

        msg = ["Unable to certify any program in the sampleset"]
        msg += [
            strings.FAILED_CERTIFICATION_NOT_ALLOWED_TO_CERTIFY.format(
                url=stat.home.get_absolute_url(), home=stat.home, program=stat.eep_program
            )
        ] * 7  # Each sampled home will fail certification
        # After Django 4.1 use this one
        # self.assertFormError(response.context["form"], field=None, errors=msg)
        self.assertFormError(response, "form", field=None, errors=msg)

    def test_sampleset_provider_test_home_certification(self):
        """This verifies we can certify a test home in a sampleset"""
        # user = self.get_admin_user(company_type="provider")
        # self.client.login(username=user.username, password='password')

        sampleset = SampleSet.objects.get(alt_name="passing ss")
        test_home = sampleset.samplesethomestatus_set.current().filter(is_test_home=True)[0]
        stat = EEPProgramHomeStatus.objects.get(id=test_home.home_status.id)
        self.assertEqual(stat.state, "certification_pending")

        user = self._get_admin_user_from_company(stat.get_provider())
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        data = {"certification_date": datetime.date.today()}
        response = self.client.post(reverse("home:certify", kwargs={"pk": stat.id}), data=data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("home:view", kwargs={"pk": stat.home.id}))

        statuses = stat.get_current_sampleset_home_statuses()
        self.assertEqual(statuses.count(), 7)
        for _stat in statuses:
            self.assertEqual(_stat.certification_date, data.get("certification_date"))
            self.assertEqual(_stat.state, "complete")

    def test_sampleset_provider_sampled_home_certification(self):
        """This verifies we can certify a sampled home in a sampleset"""

        # user = self.get_admin_user(company_type="provider")
        # self.client.login(username=user.username, password='password')

        sampleset = SampleSet.objects.get(alt_name="passing ss")
        sampled_home = sampleset.samplesethomestatus_set.current().filter(is_test_home=False)[0]
        stat = EEPProgramHomeStatus.objects.get(id=sampled_home.home_status.id)
        self.assertEqual(stat.state, "certification_pending")

        user = self._get_admin_user_from_company(stat.get_provider())
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        data = {"certification_date": datetime.date.today()}
        response = self.client.post(reverse("home:certify", kwargs={"pk": stat.id}), data=data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("home:view", kwargs={"pk": stat.home.id}))

        statuses = stat.get_current_sampleset_home_statuses()
        self.assertEqual(statuses.count(), 7)
        for _stat in statuses:
            self.assertEqual(_stat.certification_date, data.get("certification_date"))
            self.assertEqual(_stat.state, "complete")

    def test_sampleset_add_sampled_home_to_already_certification(self):
        """This verifies we can add a sample home to an already certified sampleset and certify it"""

        # Get our certified sampleset and add a new status.
        sampleset = SampleSet.objects.get(alt_name="certified ss")
        unrelated = EEPProgramHomeStatus.objects.get(home__street_line1="1 uncertified way")
        self.assertEqual(unrelated.state, "inspection")

        user = self._get_admin_user_from_company(unrelated.get_provider())
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        sampleset.add_home_status(unrelated)
        data = {"certification_date": datetime.date.today()}

        response = self.client.post(reverse("home:certify", kwargs={"pk": unrelated.id}), data=data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("home:view", kwargs={"pk": unrelated.home.id}))

        statuses = unrelated.get_current_sampleset_home_statuses()
        self.assertEqual(statuses.count(), 6)
        for _stat in statuses:
            if _stat.id == unrelated.id:
                self.assertEqual(_stat.certification_date, data.get("certification_date"))
            else:
                self.assertIsNotNone(_stat.certification_date)
            self.assertEqual(_stat.state, "complete")

    def test_sampleset_add_similar_sampled_home_to_already_certification(self):
        """This verifies we can add a sample with different (unmet) requirements we can'ts
        certify it"""

        # Get our certified sampleset and add a new status.
        sampleset = SampleSet.objects.get(alt_name="short ss")
        unrelated = EEPProgramHomeStatus.objects.get(home__street_line1="1 uncertified way")
        self.assertEqual(unrelated.state, "inspection")

        user = self._get_admin_user_from_company(unrelated.get_provider())
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        sampleset.add_home_status(unrelated)
        data = {"certification_date": datetime.date.today()}

        response = self.client.post(reverse("home:certify", kwargs={"pk": unrelated.id}), data=data)
        self.assertEqual(response.status_code, 200)

        msg = ["Unable to certify any program in the sampleset"]
        msg += [
            strings.NOT_ELIGIBLE_FOR_CERTIFICATION.format(
                url=unrelated.home.get_absolute_url(),
                home=unrelated.home,
                program=unrelated.eep_program,
            )
        ]
        # After Django 4.1 use this one
        # self.assertFormError(response.context["form"], field=None, errors=msg)
        self.assertFormError(response, "form", field=None, errors=msg)

        self.assertEqual(unrelated.state, "inspection")
        self.assertIsNone(unrelated.certification_date)


class CustomerHIRLCertificateDownloadTests(HIRLScoring2020NewConstructionTaskMixin, AxisTestCase):
    """Test HIRL certification download"""

    client_class = AxisClient

    def test_download_certificate_for_hirl_program(self):
        """
        Generate HIRL Scoring certificate with NGBS provider user
        """
        user = self.get_admin_user(company_type=Company.RATER_COMPANY_TYPE)
        eep_program_home_status = EEPProgramHomeStatus.objects.filter(
            eep_program__slug="ngbs-sf-new-construction-2020-new"
        ).first()
        eep_program_home_status.make_transition(
            transition="customer_hirl_pending_final_qa_transition"
        )
        eep_program_home_status.make_transition(
            transition="customer_hirl_certification_pending_transition"
        )
        eep_program_home_status.make_transition(transition="completion_transition", user=user)
        eep_program_home_status.certification_date = timezone.now()
        eep_program_home_status.save()

        # create Final QA
        QAStatus.objects.create(
            owner=customer_hirl_app.get_customer_hirl_provider_organization(),
            home_status=eep_program_home_status,
            requirement=QARequirement.objects.get(
                eep_program=eep_program_home_status.eep_program,
                type=QARequirement.FINAL_INSPECTION_QA_REQUIREMENT_TYPE,
            ),
            hirl_certification_level_awarded=QAStatus.GOLD_HIRL_CERTIFICATION_LEVEL_AWARDED,
            hirl_reviewer_wri_value_awarded=random.randint(0, 100),
        )

        url = reverse(
            "home:report:customer_hirl_scoring_path_certificate",
            kwargs={"pk": eep_program_home_status.pk},
        )

        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)


class CustomerHIRLWaterSenseCertificateDownloadTests(
    HIRLScoring2020NewConstructionTaskMixin, AxisTestCase
):
    """Test HIRL WaterSense certification download"""

    client_class = AxisClient

    def test_download_water_sense_certificate_for_hirl_program(self):
        """
        Generate HIRL Scoring certificate with NGBS provider user
        """
        user = self.get_admin_user(company_type=Company.RATER_COMPANY_TYPE)
        eep_program_home_status = EEPProgramHomeStatus.objects.filter(
            eep_program__slug="ngbs-sf-new-construction-2020-new"
        ).first()

        eep_program_home_status.customer_hirl_final_verifier = self.get_admin_user(
            company_type=Company.RATER_COMPANY_TYPE
        )
        eep_program_home_status.save()

        eep_program_home_status.customer_hirl_project.is_require_water_sense_certification = True
        eep_program_home_status.customer_hirl_project.save()

        eep_program_home_status.make_transition(
            transition="customer_hirl_pending_final_qa_transition"
        )
        eep_program_home_status.make_transition(
            transition="customer_hirl_certification_pending_transition"
        )
        eep_program_home_status.make_transition(transition="completion_transition", user=user)
        eep_program_home_status.certification_date = timezone.now()
        eep_program_home_status.save()

        # create Final QA
        QAStatus.objects.create(
            owner=customer_hirl_app.get_customer_hirl_provider_organization(),
            home_status=eep_program_home_status,
            requirement=QARequirement.objects.get(
                eep_program=eep_program_home_status.eep_program,
                type=QARequirement.FINAL_INSPECTION_QA_REQUIREMENT_TYPE,
            ),
            hirl_water_sense_confirmed=True,
        )

        url = reverse(
            "home:report:customer_hirl_water_sense_certificate",
            kwargs={"pk": eep_program_home_status.pk},
        )

        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)


class HomePhotoViewTests(HomeViewTestsMixins, ApiV3Tests):
    client_class = AxisClient

    def test_list_view(self):
        user = self.get_admin_user(company_type=["provider"], only_related=True)
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        home = Home.objects.filter_by_company(user.company, show_attached=True).first()

        url = reverse("home:home_photo", kwargs={"pk": home.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(url, ajax=True)
        self.assertEqual(response.status_code, 200)

    def test_create_view(self):
        user = self.get_admin_user(company_type=["provider"], only_related=True)
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        home = Home.objects.filter_by_company(user.company, show_attached=True).first()

        self.assertEqual(home.homephoto_set.count(), 0)
        url = reverse("home:home_photo", kwargs={"pk": home.pk})

        # invalid file
        with open(__file__) as f:
            response = self.client.post(url, data={"file": f, "is_primary": False})
            self.assertEqual(response.status_code, 200)
            self.assertFalse(response.json()["is_valid"])

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            image = Image.new("RGB", (200, 200), "white")
            image.save(f, "PNG")
            with open(f.name, mode="rb") as img:
                response = self.client.post(url, data={"file": img, "is_primary": False})
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.json()["is_valid"])
                self.assertTrue(response.json()["is_primary"])

    def test_set_primary(self):
        user = self.get_admin_user(company_type=["provider"], only_related=True)
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        home = Home.objects.filter_by_company(user.company, show_attached=True).first()
        home_photo = home_photo_factory(home=home)
        home_photo2 = home_photo_factory(home=home)

        self.assertEqual(home.homephoto_set.count(), 2)
        self.assertFalse(home_photo2.is_primary)

        url = reverse("home:home_photo_detail", kwargs={"pk": home.pk, "photo_pk": home_photo2.pk})

        response = self.client.post(url, data={"is_primary": True})
        self.assertEqual(response.status_code, 200)
        home_photo.refresh_from_db()
        home_photo2.refresh_from_db()
        self.assertFalse(home_photo.is_primary)
        self.assertTrue(home_photo2.is_primary)

    def test_delete_view(self):
        user = self.get_admin_user(company_type=["provider"], only_related=True)
        self.assertTrue(
            self.client.login(username=user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (user.username, user.pk),
        )

        home = Home.objects.filter_by_company(user.company, show_attached=True).first()
        home_photo = home_photo_factory(home=home)
        home_photo2 = home_photo_factory(home=home)

        self.assertEqual(home.homephoto_set.count(), 2)
        self.assertFalse(home_photo2.is_primary)
        url = reverse("home:home_photo_detail", kwargs={"pk": home.pk, "photo_pk": home_photo.pk})

        response = self.client.delete(url)
        self.assertEqual(response.status_code, 200)
        home_photo2.refresh_from_db()
        self.assertTrue(home_photo2.is_primary)


class TestBypassRoughQAActionView(AxisTestCase):
    client_class = AxisClient

    @classmethod
    def setUpTestData(cls):
        eep_program = basic_eep_program_factory(
            name="SF New Construction 2020", slug="ngbs-sf-new-construction-2020-new"
        )
        hirl_company = provider_organization_factory(
            name="Home Innovation Research Labs", slug=customer_hirl_app.CUSTOMER_SLUG
        )
        ngbs_user = provider_user_factory(
            first_name="NGBS", last_name="Admin", company=hirl_company, is_company_admin=True
        )

        provider_user_factory(
            first_name="Non", last_name="admin", company=hirl_company, is_company_admin=False
        )
        builder_organization = builder_organization_factory(name="PUG Builder")
        builder_user = builder_user_factory(is_company_admin=True, company=builder_organization)

        Relationship.objects.create_mutual_relationships(builder_organization, hirl_company)
        SponsorPreferences.objects.create(
            sponsor=hirl_company, sponsored_company=builder_organization
        )
        builder_organization.update_permissions()

        rater_organization = rater_organization_factory()
        company_admin_rater_user = rater_user_factory(
            is_company_admin=True, company=rater_organization
        )

    def setUp(self):
        builder_organization = Company.objects.filter(
            company_type=Company.BUILDER_COMPANY_TYPE
        ).first()
        eep_program = EEPProgram.objects.first()

        sf_registration = hirl_project_registration_factory(
            project_type=HIRLProjectRegistration.SINGLE_FAMILY_PROJECT_TYPE,
            builder_organization=builder_organization,
            eep_program=eep_program,
        )
        sf_project = hirl_project_factory(
            registration=sf_registration, home_address_geocode_response=None, home_status=SET_NULL
        )

        sf_registration.active()
        sf_project.create_home_status()

        update_home_states(eepprogramhomestatus_id=sf_project.home_status.id)

        super(TestBypassRoughQAActionView, self).setUp()

    def test_set_bypass_rough_qa_for_home_status(self):
        sf_project = HIRLProject.objects.first()
        ngbs_user = customer_hirl_app.get_customer_hirl_provider_organization().users.first()

        self.assertEqual(
            sf_project.home_status.state, EEPProgramHomeStatus.CUSTOMER_HIRL_PENDING_ROUGH_QA_STATE
        )

        self.assertTrue(
            self.client.login(username=ngbs_user.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (ngbs_user.username, ngbs_user.pk),
        )

        url = reverse("home:bypass_rough_qa", kwargs={"pk": sf_project.home_status.pk})

        response = self.client.get(url)
        # redirect to home view
        self.assertEqual(response.status_code, 302)
        sf_project.refresh_from_db()
        self.assertEqual(
            sf_project.home_status.state, EEPProgramHomeStatus.CUSTOMER_HIRL_PENDING_FINAL_QA_STATE
        )

        with self.subTest("Do not allow bypass with Final state"):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 403)

    def test_set_bypass_rough_qa_for_home_status_as_verifier(self):
        sf_project = HIRLProject.objects.first()

        verifier = sf_project.registration.registration_user

        self.assertEqual(
            sf_project.home_status.state, EEPProgramHomeStatus.CUSTOMER_HIRL_PENDING_ROUGH_QA_STATE
        )

        self.assertTrue(
            self.client.login(username=verifier.username, password="password"),
            msg="User %s [pk=%s] is not allowed to login" % (verifier.username, verifier.pk),
        )

        url = reverse("home:bypass_rough_qa", kwargs={"pk": sf_project.home_status.pk})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
