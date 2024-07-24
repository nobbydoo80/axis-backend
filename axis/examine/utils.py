import datetime
import logging

from django.db.models import Model
from django.db.models.fields.files import FieldFile
from django.forms import model_to_dict
from django.forms.models import ModelChoiceIteratorValue
from django.urls import reverse_lazy
from django.utils.encoding import force_str
from django.utils.functional import Promise
from hashid_field import Hashid
from phonenumbers import PhoneNumber
from rest_framework.utils.encoders import JSONEncoder

__author__ = "Autumn Valenta"
__date__ = "10-17-14  6:54 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class ExamineJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Model):
            try:
                obj = model_to_dict(obj)
            except RuntimeError as err:
                log.exception("%s [%d] JSON Encoding - %s", obj.__class__.__name__, obj.pk, err)
                return None
        elif isinstance(obj, ModelChoiceIteratorValue):
            return obj.value
        elif isinstance(obj, FieldFile):
            if obj:  # Evaluates to True if field is bound
                return obj.url
            return None
        elif isinstance(obj, datetime.tzinfo):  # django-timezone-field
            return str(obj)
        elif isinstance(obj, Promise):  # Catch reverse_lazy, among other simple things
            try:
                return force_str(obj)
            except TypeError:
                return repr(list(map(str, obj)))  # I have no idea why I can't serializer this list
        elif isinstance(obj, PhoneNumber):
            return str(obj)
        elif isinstance(obj, Exception):
            raise obj
        elif isinstance(obj, Hashid):
            return str(obj)
        return super(ExamineJSONEncoder, self).default(obj)


def template_url(t):
    """
    Generate a full AJAX URL to the template.  Instead of assuming a global prefix for template
    paths, the template name is put into the urlresolver to allow the project to configure where
    those templates are served.

    The default url provided in ``examine/urls.py`` sets this prefix to match the actual app name,
    allowing the url prefix and the template name prefix to match, both being ``"examine/"``.

    Other configurations could define the named url to have some extra prefix, or additionally
    subclass the ``examine.views.TemplatePreprocessorView`` view to allow some other prefix that is
    not part of the template path at all.
    """
    return reverse_lazy("examine:template", kwargs={"template": t})
