from .config import VerifierEnrollmentConfig

__author__ = "Artem Hruzd"
__date__ = "04/16/2020 16:55"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

STATE_LABEL = "Enrollment Status"

MANAGEMENT_LABELS = {
    "agreement_start_date": "Start Date",
    "agreement_expiration_date": "Expiration Date",
    "agreement_verifier_id": "NGBS Verifier ID",
}
MANAGEMENT_FIELDS = tuple(MANAGEMENT_LABELS.keys())

ENROLLMENT_LABELS = {
    "applicant_first_name": "First Name",
    "applicant_last_name": "Last Name",
    "applicant_title": "Title",
    "applicant_phone_number": "Phone Number",
    "applicant_cell_number": "Cell Number",
    "applicant_email": "Email Address",
    "administrative_contact_first_name": "First Name",
    "administrative_contact_last_name": "Last Name",
    "administrative_contact_phone_number": "Phone Number",
    "administrative_contact_email": "Email Address",
    "company_with_multiple_verifiers": "Click this checkbox if you work for a company with multiple Verifiers as contact information for a company officer will be required",
    "company_officer_first_name": "First Name",
    "company_officer_last_name": "Last Name",
    "company_officer_phone_number": "Phone Number",
    "company_officer_title": "Title",
    "company_officer_email": "Email",
    "provided_services": "Provided Services",
    "us_states": "Geographic Areas Served",
}
ENROLLMENT_FIELDS = tuple(ENROLLMENT_LABELS.keys())
