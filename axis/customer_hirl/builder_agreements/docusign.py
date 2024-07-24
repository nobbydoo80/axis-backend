"""DocuSign transport declarations."""

__author__ = "Steven Klass"
__date__ = "06/15/2019 12:50"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

import logging

from django.apps import apps

from axis.filehandling import docusign

log = logging.getLogger(__name__)
customer_hirl_app = apps.get_app_config("customer_hirl")


class HIRLDocuSignObject(docusign.DocuSignObject):
    def __init__(self, user_id=None, account_id=None, **kwargs):
        super(HIRLDocuSignObject, self).__init__(
            user_id=customer_hirl_app.DOCUSIGN_USER_ID,
            account_id=customer_hirl_app.DOCUSIGN_ACCOUNT_ID,
            **kwargs,
        )


class HIRLBaseDocuSignDeclarativeTemplate(docusign.DocuSignDeclarativeTemplate):
    def __init__(self, user_id=None, account_id=None, **kwargs):
        super(HIRLBaseDocuSignDeclarativeTemplate, self).__init__(
            user_id=customer_hirl_app.DOCUSIGN_USER_ID,
            account_id=customer_hirl_app.DOCUSIGN_ACCOUNT_ID,
            **kwargs,
        )


class UnsignedBuilderAgreement(HIRLBaseDocuSignDeclarativeTemplate):
    """Unsigned Builder Agreement for signing"""

    email_subject = "NGBS Client Agreement for {company}: Signing Required"
    email_message = """
        Dear NGBS Green Client<br/>
        <br/>
        Thank you for selecting NGBS Green certification for your project.<br/>
        <br/>
        <b>Agreement</b><br/>
        NGBS Green certification requires the client that is <u>financially responsible</u> for the
        project(s) to sign an agreement with Home Innovation Research Labs. The client is
        typically the builder, developer, or building owner. The signatory must be an <u>Officer of
        the Company</u> or someone who can commit the company to meeting the agreement’s
        requirements. Agreements are valid for four years. Only one agreement is needed, even if
        you have multiple projects seeking certification. However, if you use a different entity
        name, such as an LLC, for a project(s), then you must sign an agreement for each entity.
        <br/>
        <br/>
        <b>Insurance</b><br/>
        Each client must have at least $1M in general liability insurance and Home Innovation
        must be listed as an “additional insured.” Insurance must be maintained during
        construction and until the project is certified. Because insurance is renewed annually,
        clients must upload an updated certificate of insurance (COI) after each renewal
        until the project is certified.<br/>
        <br/>
        More details are available in the <a
        href="https://www.homeinnovation.com/~/media/F0468499013A432BAEA6A84325380019.pdf">
        Builders Resource Guide</a>; if you have any questions or concerns, please <a
        href="https://www.homeinnovation.com/about/contact_us?drop=green%20building%20certification">
        Contact us</a>.<br/>
    """
    signers = [
        {
            "kwarg": "user",
            "page": 4,
            "coordinates": (130, 238),
            "fields": {
                "Date": {
                    "page": 4,
                    "coordinates": (205, 290),
                    "type": "date_signed_tabs",
                },
                "Name": {
                    "page": 4,
                    "coordinates": (130, 308),
                    "type": "text_tabs",
                },
                "Title": {
                    "page": 4,
                    "coordinates": (130, 338),
                    "type": "text_tabs",
                },
            },
        },
    ]


class UnsignedBuilderAgreementV2(UnsignedBuilderAgreement):
    signers = [
        {
            "kwarg": "user",
            "page": 4,
            "coordinates": (130, 372),
            "fields": {
                "Date": {
                    "page": 4,
                    "coordinates": (205, 435),
                    "type": "date_signed_tabs",
                },
                "Name": {
                    "page": 4,
                    "coordinates": (130, 451),
                    "type": "text_tabs",
                },
                "Title": {
                    "page": 4,
                    "coordinates": (130, 485),
                    "type": "text_tabs",
                },
            },
        },
    ]


class UnsignedBuilderAgreementV3(UnsignedBuilderAgreement):
    signers = [
        {
            "kwarg": "user",
            "page": 4,
            "coordinates": (130, 425),
            "fields": {
                "Date": {
                    "page": 4,
                    "coordinates": (205, 481),
                    "type": "date_signed_tabs",
                },
                "Name": {
                    "page": 4,
                    "coordinates": (130, 500),
                    "type": "text_tabs",
                },
                "Title": {
                    "page": 4,
                    "coordinates": (130, 534),
                    "type": "text_tabs",
                },
            },
        },
    ]


class UnsignedBuilderAgreementV4(UnsignedBuilderAgreement):
    signers = [
        {
            "kwarg": "user",
            "page": 4,
            "coordinates": (130, 370),
            "fields": {
                "Date": {
                    "page": 4,
                    "coordinates": (205, 426),
                    "type": "date_signed_tabs",
                },
                "Name": {
                    "page": 4,
                    "coordinates": (130, 447),
                    "type": "text_tabs",
                },
                "Title": {
                    "page": 4,
                    "coordinates": (130, 477),
                    "type": "text_tabs",
                },
            },
        },
    ]


class CountersigningBuilderAgreement(HIRLBaseDocuSignDeclarativeTemplate):
    """Builder Agreement for countersigning"""

    email_subject = "NGBS Client Agreement for {company}: Counter-signing Required"
    email_message = """
        The legal agreement for {company} is awaiting your counter-signature.

        Thank you,

        NGBS Program Staff
    """
    signers = [
        {
            "kwarg": "user",
            "page": 4,
            "coordinates": (130, 105),
            "fields": {
                "Date": {
                    "page": 4,
                    "coordinates": (205, 157),
                    "type": "date_signed_tabs",
                },
                "Name": {
                    "page": 4,
                    "coordinates": (130, 178),
                    "type": "text_tabs",
                    "value": "William M. Ingley",
                    "locked": True,
                },
                "Title": {
                    "page": 4,
                    "coordinates": (130, 209),
                    "type": "text_tabs",
                    "value": "Vice President and CFO",
                    "locked": True,
                },
            },
        },
    ]


class CountersigningBuilderAgreementV2(CountersigningBuilderAgreement):
    signers = [
        {
            "kwarg": "user",
            "page": 4,
            "coordinates": (130, 237),
            "fields": {
                "Date": {
                    "page": 4,
                    "coordinates": (205, 301),
                    "type": "date_signed_tabs",
                },
                "Name": {
                    "page": 4,
                    "coordinates": (130, 321),
                    "type": "text_tabs",
                    "value": "William M. Ingley",
                    "locked": True,
                },
                "Title": {
                    "page": 4,
                    "coordinates": (130, 354),
                    "type": "text_tabs",
                    "value": "Vice President and CFO",
                    "locked": True,
                },
            },
        },
    ]


class CountersigningBuilderAgreementV3(CountersigningBuilderAgreement):
    signers = [
        {
            "kwarg": "user",
            "page": 4,
            "coordinates": (130, 286),
            "fields": {
                "Date": {
                    "page": 4,
                    "coordinates": (205, 348),
                    "type": "date_signed_tabs",
                },
                "Name": {
                    "page": 4,
                    "coordinates": (130, 368),
                    "type": "text_tabs",
                    "value": "William M. Ingley",
                    "locked": True,
                },
                "Title": {
                    "page": 4,
                    "coordinates": (130, 401),
                    "type": "text_tabs",
                    "value": "Vice President and CFO",
                    "locked": True,
                },
            },
        },
    ]


class CountersigningBuilderAgreementV4(CountersigningBuilderAgreement):
    signers = [
        {
            "kwarg": "user",
            "page": 4,
            "coordinates": (130, 231),
            "fields": {
                "Date": {
                    "page": 4,
                    "coordinates": (205, 293),
                    "type": "date_signed_tabs",
                },
                "Name": {
                    "page": 4,
                    "coordinates": (130, 313),
                    "type": "text_tabs",
                    "value": "William M. Ingley",
                    "locked": True,
                },
                "Title": {
                    "page": 4,
                    "coordinates": (130, 346),
                    "type": "text_tabs",
                    "value": "Vice President and CFO",
                    "locked": True,
                },
            },
        },
    ]


class UnsignedExtensionRequestAgreement(HIRLBaseDocuSignDeclarativeTemplate):
    """Unsigned Extension Request Agreement for signing"""

    email_subject = "NGBS Extension Request Agreement for {company}: Signing Required"
    email_message = """
        Dear NGBS Green Client<br/>
        <br/>
        Thank you for selecting NGBS Green certification for your project.<br/>
        <br/>
        <b>Agreement</b><br/>
        NGBS Green certification requires the client that is <u>financially responsible</u> for the project(s) 
        to sign an agreement with Home Innovation Research Labs. 
        The client is typically the builder, developer, or building owner. 
        The Signatory must be an <u>Officer of the Company</u> or someone who can commit the company to meeting 
        the agreement’s requirements. Only one agreement is needed, even if you have multiple projects seeking 
        certification. However, if you use a different entity name, such as an LLC, for a project(s), 
        then you must sign an agreement for each entity.
        <br/>
        <br/>
        You have elected to pursue an extension to your existing four-year agreement. 
        This extension will make your existing agreement valid for an additional two years.
        <br/>
        <br/>
        <b>Insurance</b><br/>
        Each client must have at least $1M in general liability insurance and Home Innovation
        must be listed as an “additional insured.” Insurance must be maintained during
        construction and until the project is certified. Because insurance is renewed annually,
        clients must upload an updated certificate of insurance (COI) after each renewal
        until the project is certified.<br/>
        <br/>
        More details are available in the <a
        href="https://www.homeinnovation.com/~/media/F0468499013A432BAEA6A84325380019.pdf">
        Builders Resource Guide</a>; if you have any questions or concerns, please <a
        href="https://www.homeinnovation.com/about/contact_us?drop=green%20building%20certification">
        Contact us</a>.<br/>
    """
    signers = [
        {
            "kwarg": "user",
            "page": 1,
            "coordinates": (130, 322),
            "fields": {
                "Date": {
                    "page": 1,
                    "coordinates": (216, 386),
                    "type": "date_signed_tabs",
                },
                "Name": {
                    "page": 1,
                    "coordinates": (144, 405),
                    "type": "text_tabs",
                },
                "Title": {
                    "page": 1,
                    "coordinates": (144, 440),
                    "type": "text_tabs",
                },
            },
        },
    ]


class CountersigningExtensionRequestAgreement(HIRLBaseDocuSignDeclarativeTemplate):
    """
    Extension request Agreement for countersigning
    """

    email_subject = "NGBS Extension Request Agreement for {company}: Counter-signing Required"
    email_message = """
        The extension request agreement for {company} is awaiting your counter-signature.

        Thank you,

        NGBS Program Staff
    """
    signers = [
        {
            "kwarg": "user",
            "page": 1,
            "coordinates": (144, 196),
            "fields": {
                "Date": {
                    "page": 1,
                    "coordinates": (216, 248),
                    "type": "date_signed_tabs",
                },
                "Name": {
                    "page": 1,
                    "coordinates": (145, 268),
                    "type": "text_tabs",
                    "value": "William M. Ingley",
                    "locked": True,
                },
                "Title": {
                    "page": 1,
                    "coordinates": (145, 301),
                    "type": "text_tabs",
                    "value": "Vice President and CFO",
                    "locked": True,
                },
            },
        },
    ]
