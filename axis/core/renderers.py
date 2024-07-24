"""renderers.py: """

__author__ = "Artem Hruzd"
__date__ = "01/04/2020 13:52"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


from rest_framework.renderers import BrowsableAPIRenderer, BaseRenderer


class NoHTMLFormBrowsableAPIRenderer(BrowsableAPIRenderer):
    def get_filter_form(self, data, view, request):
        """
        Disable Django-filters form because FK fields are too heavy
        :param data:
        :param view:
        :param request:
        :return:
        """
        return None

    def get_rendered_html_form(self, *args, **kwargs):
        """
        We don't want the HTML forms to be rendered because it can be
        really slow with large datasets
        """
        return None


class BinaryFileRenderer(BaseRenderer):
    media_type = "application/octet-stream"
    format = None
    charset = None
    render_style = "binary"

    def render(self, data, media_type=None, renderer_context=None):
        return data
