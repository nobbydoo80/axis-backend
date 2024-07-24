"""checks.py: """

__author__ = "Artem Hruzd"
__date__ = "07/25/2019 18:28"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

import os
import re
import reportlab

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.checks import register, Tags, Warning, Error
from reportlab.pdfbase import pdfmetrics
from django.db.models import Q
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.pdfbase.ttfonts import TTFont


from . import technology


class ChecksConfig(technology.ExtensionConfig):
    def ready(self):
        """Register django system checks for optional dependencies."""
        super(ChecksConfig, self).ready()

        register(Tags.compatibility)(rabbitmq_check)
        register(Tags.compatibility)(default_field_encryption_key_check)
        register(Tags.compatibility)(register_reportlab_fonts)
        register(Tags.compatibility)(production_data_in_database_check)


def rabbitmq_check(**_kwargs):
    """Verify that RabbitMQ is functioning"""
    from django.conf import settings
    import socket

    def _sanitize(url):
        match = re.search(r"(.*:)(.*)(@[a-zA-Z0-9\.]+)(:.*)", url)
        if match:
            return (
                match.group(1)
                + "".join(["*" for x in match.group(2)])
                + match.group(3)
                + match.group(4)
            )
        return url

    errors = []
    always_eager = getattr(settings, "CELERY_TASK_ALWAYS_EAGER", False)
    if not always_eager and getattr(settings, "CELERY_BROKER_URL"):
        match = re.search(r"@([a-zA-Z0-9\.]+):(\d+)(/.*)", settings.CELERY_BROKER_URL)
        if match:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            try:
                s.connect((match.group(1), int(match.group(2))))
                s.shutdown(socket.SHUT_RDWR)
            except (socket.timeout, socket.error):
                errors.append(
                    Warning(
                        "CELERY_TASK_ALWAYS_EAGER=False and unable to connect to RabbitMQ on %s"
                        % _sanitize(settings.CELERY_BROKER_URL),
                        hint="Set CELERY_TASK_ALWAYS_EAGER=True or start RabbitMQ on %s:%s"
                        % (match.group(1), match.group(2)),
                        id="core.E002",
                    )
                )
            finally:
                s.close()
        else:
            from kombu import Connection
            from kombu.exceptions import OperationalError

            try:
                conn = Connection(settings.CELERY_BROKER_URL)
                conn.ensure_connection(max_retries=2)
            except OperationalError:
                errors.append(
                    Warning(
                        "CELERY_TASK_ALWAYS_EAGER=True and unable to connect to RabbitMQ on %s"
                        % _sanitize(settings.CELERY_BROKER_URL),
                        hint="Set CELERY_TASK_ALWAYS_EAGER=False or start RabbitMQ",
                        id="core.E003",
                    )
                )
    return errors


def default_field_encryption_key_check(**_kwargs):
    """Verify the default encryption key is not used"""
    errors = []
    if settings.FIELD_ENCRYPTION_KEY == "nnnMOp6xF172kZGttkvZYb38ewR0-79O0ii_VzRYhWg=":
        errors.append(
            Warning(
                "FIELD_ENCRYPTION_KEY settings variable is set to a default value",
                hint="Run ./manage.py generate_encryption_key and save the value to your .env",
                id="core.E004",
            )
        )
    return errors


def register_reportlab_fonts(**kwargs):
    """
    Register all custom fonts for pdfmetrics in one place
    :return:
    """
    errors = []
    font_dir = os.path.join(settings.SITE_ROOT, "axis", "core", "static", "font")

    fonts_map = {
        "MuseoSans-100": "MuseoSans-100.ttf",
        "MuseoSans-500": "MuseoSans-500.ttf",
        "Arial": "Arial.ttf",
        "Arial-Bold": "Arial-Bold.ttf",
        "Arial-Italic": "Arial-Italic.ttf",
        "Arial-BoldItalic": "Arial-Bold-Italic.ttf",
        "Arial-Black": "Arial-Black.ttf",
        "Archer": "Tahoma.ttf",
        "Archer-Bold": "Tahoma-Bold.ttf",
        "Times New Roman": "times-new-roman.ttf",
    }

    for font_name, font_file_name in fonts_map.items():
        try:
            pdfmetrics.registerFont(
                TTFont(font_name, os.path.normpath(os.path.join(font_dir, font_file_name)))
            )
        except (ValueError, reportlab.pdfbase.ttfonts.TTFError) as exc:
            errors.append(
                Warning(
                    f"Cannot register custom font for pdfmetrics",
                    hint=f"{exc}",
                    id="core.E005",
                )
            )

    registerFontFamily(
        "Arial",
        normal="Arial",
        bold="Arial-Bold",
        italic="Arial-Italic",
        boldItalic="Arial-BoldItalic",
    )
    return errors


def production_data_in_database_check(**kwargs):
    errors = []

    if settings.SERVER_TYPE != settings.LOCALHOST_SERVER_TYPE:
        return []

    real_emails = [
        "Matt@momentumidaho.com",
        "verificationreport@homeinnovation.com",
        "kent@swiftsureenergy.com",
        "lpearcy@15lightyears.com",
    ]

    conditions = Q()
    for email in real_emails:
        conditions |= Q(email__icontains=email)
    emails = get_user_model().objects.filter(conditions).values_list("email", flat=True)

    if emails:
        errors.append(
            Error(
                f"Real emails: {list(emails)} exist in development database. "
                f"Sanitize database from production data first.",
                hint=f"Use manage.py set_fake_emails command",
                id="core.E006",
            )
        )

    return errors
