"""renderer.py: """

__author__ = "Artem Hruzd"
__date__ = "01/06/2020 12:22"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

from drf_yasg.renderers import SwaggerUIRenderer


class AxisSwaggerUIRenderer(SwaggerUIRenderer):
    template = "drf-yasg/swagger-ui.html"
