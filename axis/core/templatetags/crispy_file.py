from django.conf import settings
from django import forms
from django.forms.fields import ChoiceField
from django.template.loader import render_to_string
from django import template

from crispy_forms.exceptions import CrispyError

__author__ = "Steven Klass"
__date__ = "1/20/12 1:28 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

TEMPLATE_PACK = getattr(settings, "CRISPY_TEMPLATE_PACK", "bootstrap")
DEBUG = getattr(settings, "DEBUG", False)

register = template.Library()


@register.simple_tag(name="crispy_file_field")
def crispy_file_field(field, disable_removal=True, template_pack=TEMPLATE_PACK):
    return render_to_string(
        "%s/file_field.html" % template_pack,
        {
            "field": field,
            "form_show_errors": True,
            "disable_removal": disable_removal,
        },
    )


@register.filter(name="as_crispy_file_field")
def as_crispy_file_field(field, template_pack=TEMPLATE_PACK):
    """
    Renders a form field like a django-crispy-forms field::

        {% load crispy_forms_tags %}
        {{ form.field|as_crispy_field }}
        or
        {{ form.field|as_crispy_field:"bootstrap" }}
    """
    if not isinstance(field, forms.BoundField) and DEBUG:
        raise CrispyError("|as_crispy_file_field got passed an invalid or inexistent field")

    if field.field.widget.input_type != "file":
        raise CrispyError("|as_crispy_file_field requires a file field")

    return render_to_string(
        "%s/file_field.html" % template_pack,
        {
            "field": field,
            "form_show_errors": True,
        },
    )


@register.filter(name="as_crispy_field_no_label")
def as_crispy_field_no_label(field, template_pack=TEMPLATE_PACK):
    """
    Renders a form field like a django-crispy-forms field::

        {% load crispy_forms_tags %}
        {{ form.field|as_crispy_field }}
        or
        {{ form.field|as_crispy_field:"bootstrap" }}
    """
    if not isinstance(field, forms.BoundField) and DEBUG:
        raise CrispyError("|as_crispy_field got passed an invalid or inexistent field")

    return render_to_string(
        "%s/field.html" % template_pack,
        {
            "field": field,
            "form_show_errors": True,
            "form_show_labels": False,
        },
    )


@register.simple_tag(takes_context=True, name="crispy_checklist_field")
def crispy_checklist_field(context, field, template_pack=TEMPLATE_PACK):
    if isinstance(field.field, ChoiceField):
        return render_to_string(
            "%s/radio.html" % template_pack,
            {
                "field": field,
                "question": context["question"],
            },
        )

    return render_to_string(
        "%s/field.html" % template_pack,
        {
            "field": field,
            "form_show_errors": True,
            "form_show_labels": False,
        },
    )
