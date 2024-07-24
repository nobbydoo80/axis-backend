"""mixins.py: Django checklist"""


import logging

from django.contrib import messages

__author__ = "Michael Jeffrey"
__date__ = "5/27/13 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


# NOTE: Django 1.6 added automatic interpolation of object.__dict__ into the success_message string,
# but this was something we used since Django 1.4.  Most of our messages just drop the object
# directly into the format string ("{instance} updated"), this is being left in play even though
# we're on Django 1.6 now.
class BaseFormMessagingMixin(object):
    """Provides automatic string formatting to the view's ``success_message`` string."""

    success_message = "Success."
    error_message = "Error saving: see below."

    def _get_message(self, message_type, form):
        if message_type not in ("error", "success"):
            raise ValueError("Invalid message type %r" % message_type)
        message = getattr(self, "{}_message".format(message_type), message_type.capitalize())
        format_args = getattr(self, "get_{}_message_args".format(message_type))(form)
        if isinstance(format_args, dict):
            message = message.format(**format_args)
        else:
            message = message.format(*format_args)
        return message

    def get_success_message(self, form):
        return self._get_message("success", form)

    def get_success_message_args(self, form):
        return {"instance": form.instance}

    def get_error_message(self, form):
        return self._get_message("error", form)

    def get_error_message_args(self, form):
        return ()


class FormMessagingMixin(BaseFormMessagingMixin):
    def form_valid(self, form):
        response = super(FormMessagingMixin, self).form_valid(form)
        messages.success(self.request, self.get_success_message(form))
        return response

    def form_invalid(self, form):
        response = super(FormMessagingMixin, self).form_invalid(form)
        messages.error(self.request, self.get_error_message(form))
        return response


class FormsetMessagingMixin(BaseFormMessagingMixin):
    def get_success_message_args(self, formset):
        return {
            "changed_objects": formset.changed_objects,
            "num_changed_objects": len(formset.changed_objects),
            "deleted_objects": formset.deleted_objects,
            "num_deleted_objects": len(formset.deleted_objects),
            "new_objects": formset.new_objects,
            "num_new_objects": len(formset.new_objects),
            "formset": formset,
        }

    def formset_valid(self, formset):
        response = super(FormsetMessagingMixin, self).formset_valid(formset)
        messages.success(self.request, self.get_success_message(formset))
        return response

    def formset_invalid(self, formset):
        response = super(FormsetMessagingMixin, self).formset_invalid(formset)
        messages.error(self.request, self.get_error_message(formset))
        return response


class MultiFormMessagingMixin(BaseFormMessagingMixin):
    """Implements automatic messaging calls for the ``extra_views`` multi-form views."""

    def get_success_message_args(self, forms):
        return forms

    def valid_all(self, forms):
        messages.success(self.request, self.get_success_message(forms))

    def forms_invalid(self, forms):
        response = super(MultiFormMessagingMixin, self).forms_invalid(forms)
        messages.error(self.request, self.get_error_message(forms))
        return response
