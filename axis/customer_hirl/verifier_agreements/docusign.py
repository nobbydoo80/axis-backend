"""DocuSign transport declarations."""


import logging

from axis.customer_hirl.builder_agreements.docusign import HIRLBaseDocuSignDeclarativeTemplate

__author__ = "Steven Klass"
__date__ = "06/15/2019 12:50"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class UnsignedVerifierAgreement(HIRLBaseDocuSignDeclarativeTemplate):
    """Unsigned Verifier Agreement for signing"""

    email_subject = "NGBS Verifier Agreement for {verifier}: Signing Required"
    email_message = """
        Dear Prospective NGBS Green Verifier<br/>
        <br/>
        Thank you for choosing to become an NGBS Green Verifier.<br/>
        <br/>
        <b>Verifier Agreement</b><br/>
        NGBS Green certification requires a prospective Verifier to sign an agreement with Home
        Innovation. The Verifier Agreement must also be signed by an Officer of the Verifier Company
        and/or someone who can commit the company to meeting the Verifier agreement’s requirements.
        Agreements are valid for four years. <br/>
        <br/>
        <b>Insurance</b><br/>
        Minimum insurance coverage is required while conducting verification services for Home
        Innovation. Accredited NGBS Green Verifiers are required to submit evidence of their
        insurance coverage to Home Innovation on an annual basis. Failure to demonstrate insurance
        coverage may result in termination of verifier accreditation. “Home Innovation Research
        Labs” must be listed as an additional insured. Required coverage is shown in the <a
        href="https://www.homeinnovation.com/-/media/Files/Certification/Green_Building/NGBS-Greeen-Verifier-Candidate-Handbook.pdf">
        NGBS Green Verifier Candidate Handbook</a>.<br/>
        <br/>
        If you have any questions or concerns, please <a
        href="https://www.homeinnovation.com/about/contact_us?drop=green%20building%20certification">
        Contact us</a>.<br/>
    """
    signers = [
        {
            "kwarg": "verifier",
            "page": 6,
            "coordinates": (335, 224),
            "fields": {
                "line1": {
                    "page": 5,
                    "coordinates": (69, 259),
                    "type": "text_tabs",
                    "dimensions": (245, 8),
                    "font_size": "size8",
                },
                "line2": {
                    "page": 5,
                    "coordinates": (69, 271),
                    "type": "text_tabs",
                    "dimensions": (245, 8),
                    "font_size": "size8",
                },
                "line3": {
                    "page": 5,
                    "coordinates": (69, 283),
                    "type": "text_tabs",
                    "dimensions": (245, 8),
                    "font_size": "size8",
                },
                "attn": {
                    "page": 5,
                    "coordinates": (95, 295),
                    "type": "text_tabs",
                    "dimensions": (211, 8),
                    "font_size": "size8",
                },
                "email": {
                    "page": 5,
                    "coordinates": (100, 308),
                    "type": "text_tabs",
                    "dimensions": (207, 8),
                    "font_size": "size8",
                },
                "Date": {
                    "page": 6,
                    "coordinates": (435, 285),
                    "type": "date_signed_tabs",
                },
            },
        },
    ]


class UnsignedVerifierAgreementV2(UnsignedVerifierAgreement):
    """Unsigned Verifier Agreement for signing V2"""

    signers = [
        {
            "kwarg": "verifier",
            "page": 6,
            "coordinates": (335, 380),
            "fields": {
                "line1": {
                    "page": 5,
                    "coordinates": (320, 179),
                    "type": "text_tabs",
                    "dimensions": (245, 8),
                    "font_size": "size8",
                },
                "line2": {
                    "page": 5,
                    "coordinates": (320, 191),
                    "type": "text_tabs",
                    "dimensions": (245, 8),
                    "font_size": "size8",
                },
                "line3": {
                    "page": 5,
                    "coordinates": (320, 203),
                    "type": "text_tabs",
                    "dimensions": (245, 8),
                    "font_size": "size8",
                },
                "attn": {
                    "page": 5,
                    "coordinates": (346, 214),
                    "type": "text_tabs",
                    "dimensions": (211, 8),
                    "font_size": "size8",
                },
                "email": {
                    "page": 5,
                    "coordinates": (350, 226),
                    "type": "text_tabs",
                    "dimensions": (207, 8),
                    "font_size": "size8",
                },
                "Date": {
                    "page": 6,
                    "coordinates": (435, 437),
                    "type": "date_signed_tabs",
                },
            },
        },
    ]


class UnsignedOfficerAgreement(UnsignedVerifierAgreement):
    """Unsigned Officer Agreement for signing"""

    email_subject = "NGBS Verifier Agreement for {officer}: Signing Required"

    signers = [
        {
            "kwarg": "officer",
            "page": 6,
            "coordinates": (335, 367),
            "fields": {
                "Date": {
                    "page": 6,
                    "coordinates": (435, 430),
                    "type": "date_signed_tabs",
                }
            },
        },
    ]


class UnsignedOfficerAgreementV2(UnsignedVerifierAgreement):
    """Unsigned Officer Agreement for signing V2"""

    email_subject = "NGBS Verifier Agreement for {officer}: Signing Required"

    signers = [
        {
            "kwarg": "officer",
            "page": 6,
            "coordinates": (335, 517),
            "fields": {
                "Date": {
                    "page": 6,
                    "coordinates": (435, 573),
                    "type": "date_signed_tabs",
                }
            },
        },
    ]


class CountersigningVerifierAgreement(HIRLBaseDocuSignDeclarativeTemplate):
    """Verifier Agreement for countersigning"""

    email_subject = "NGBS Verifier Agreement for {countersigning_user}: Counter-signing Required"
    email_message = """
        The legal agreement for {countersigning_user} is awaiting your counter-signature.

        Thank you,

        NGBS Program Staff
    """
    signers = [
        {
            "kwarg": "countersigning_user",
            "page": 6,
            "coordinates": (335, 90),
            "fields": {
                "Date": {
                    "page": 6,
                    "coordinates": (435, 150),
                    "type": "date_signed_tabs",
                }
            },
        },
    ]


class CountersigningVerifierAgreementV2(CountersigningVerifierAgreement):
    """Verifier Agreement for countersigning V2"""

    signers = [
        {
            "kwarg": "countersigning_user",
            "page": 6,
            "coordinates": (335, 245),
            "fields": {
                "Date": {
                    "page": 6,
                    "coordinates": (435, 304),
                    "type": "date_signed_tabs",
                }
            },
        },
    ]
