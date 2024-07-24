"""UI labels and choice sets."""


__author__ = "Autumn Valenta"
__date__ = "10/10/2018 5:00 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]

STATE_LABEL = "Enrollment Status"

MANAGEMENT_LABELS = {
    "agreement_start_date": "Start Date",
    "agreement_expiration_date": "Expiration Date",
}
MANAGEMENT_FIELDS = tuple(MANAGEMENT_LABELS.keys())

ENROLLMENT_LABELS = {
    "website": "Website",
    "use_payment_contact_in_ngbs_green_projects": (
        "Should this person be contacted for payment on future NGBS Green projects?"
    ),
    "primary_contact_first_name": "First Name",
    "primary_contact_last_name": "Last Name",
    "primary_contact_title": "Title",
    "primary_contact_phone_number": "Phone Number",
    "primary_contact_cell_number": "Cell Number",
    "primary_contact_email_address": "Email Address",
    "secondary_contact_first_name": "First Name",
    "secondary_contact_last_name": "Last Name",
    "secondary_contact_title": "Title",
    "secondary_contact_phone_number": "Phone Number",
    "secondary_contact_cell_number": "Cell Number",
    "secondary_contact_email_address": "Email Address",
    "payment_contact_first_name": "First Name",
    "payment_contact_last_name": "Last Name",
    "payment_contact_title": "Title",
    "payment_contact_phone_number": "Phone Number",
    "payment_contact_cell_number": "Cell Number",
    "payment_contact_email_address": "Email Address",
    "marketing_contact_first_name": "First Name",
    "marketing_contact_last_name": "Last Name",
    "marketing_contact_title": "Title",
    "marketing_contact_phone_number": "Phone Number",
    "marketing_contact_cell_number": "Cell Number",
    "marketing_contact_email_address": "Email Address",
    "website_contact_first_name": "First Name",
    "website_contact_last_name": "Last Name",
    "website_contact_title": "Title",
    "website_contact_phone_number": "Phone Number",
    "website_contact_cell_number": "Cell Number",
    "website_contact_email_address": "Email Address",
}
ENROLLMENT_FIELDS = tuple(ENROLLMENT_LABELS.keys())
ENROLLMENT_REQUIRED_FIELDS = (
    "primary_contact_first_name",
    "primary_contact_last_name",
    "primary_contact_title",
    "primary_contact_phone_number",
    "primary_contact_email_address",
    "marketing_contact_first_name",
    "marketing_contact_last_name",
    "marketing_contact_title",
    "marketing_contact_phone_number",
    "marketing_contact_email_address",
    "website_contact_first_name",
    "website_contact_last_name",
    "website_contact_title",
    "website_contact_phone_number",
)
