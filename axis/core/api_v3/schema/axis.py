"""schema.py: """

__author__ = "Artem Hruzd"
__date__ = "07/14/2020 21:46"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

import time
import functools
import json
import logging
import operator
from collections import namedtuple, defaultdict
from typing import List, Optional, AnyStr

from drf_yasg.generators import OpenAPISchemaGenerator
from drf_yasg.inspectors import SwaggerAutoSchema
from rest_framework.permissions import OperandHolder, SingleOperandHolder

from axis.core.api_v3.options import AxisFrontEndOptions


class AxisOpenAPISchemaGenerator(OpenAPISchemaGenerator):
    def get_endpoints(self, request):
        """Iterate over all the registered endpoints in the API and return a fake view with the right parameters.

        Custom representation also calculate time for long-running views(greater than 1 sec)

        :param request: request to bind to the endpoint views
        :type request: rest_framework.request.Request or None
        :return: {path: (view_class, list[(http_method, view_instance)])
        :rtype: dict[str,(type,list[(str,rest_framework.views.APIView)])]
        """
        enumerator = self.endpoint_enumerator_class(
            self._gen.patterns, self._gen.urlconf, request=request
        )
        endpoints = enumerator.get_api_endpoints()

        view_paths = defaultdict(list)
        view_cls = {}
        for path, method, callback in endpoints:
            start_time = time.time()
            view = self.create_view(callback, method, request)
            path = self.coerce_path(path, view)
            view_paths[path].append((method, view))
            view_cls[path] = callback.cls
            end_time = round(time.time() - start_time)
            if end_time > 1:
                logging.warning(f"{view} {path} {method} {end_time}")
        return {path: (view_cls[path], methods) for path, methods in view_paths.items()}


PermissionItem = namedtuple("PermissionItem", ["name", "doc_str"])


class AxisSchema(SwaggerAutoSchema):
    # https://github.com/axnsan12/drf-yasg/issues/358
    def get_summary_and_description(self):
        """
        Return summary and description extended with permission docs.
        """
        summary, description = super().get_summary_and_description()
        permissions_description = self._get_permissions_description()
        if permissions_description:
            description += permissions_description

        if self.method == "GET":
            frontend_options = AxisFrontEndOptions(request=self.request, view=self.view)
            description += "\n\n**Front-end Available elements:**\n"
            available_element_options = frontend_options.get_available_elements()
            description += self._render_json(data=available_element_options)

            description += "\n\n**Front-end Permissions:**\n"
            available_permision_options = frontend_options.determine_permissions()
            description += self._render_json(data=available_permision_options)

        return summary, description

    def _handle_permission(self, permission_class) -> Optional[PermissionItem]:
        permission = None

        try:
            permission = PermissionItem(
                permission_class.__name__,
                permission_class.get_description(self.view),
            )
        except AttributeError:
            if permission_class.__doc__:
                permission = PermissionItem(
                    permission_class.__name__,
                    permission_class.__doc__.replace("\n", " ").strip(),
                )

        return permission

    def _handle_operation_holder(self, permission_class) -> List[PermissionItem]:
        if isinstance(permission_class, OperandHolder):
            items = [
                self._handle_operation_holder(permission_class.op1_class),
                self._handle_operation_holder(permission_class.op2_class),
            ]
            flat_items = functools.reduce(operator.concat, items)
            return flat_items

        if isinstance(permission_class, SingleOperandHolder):
            return [
                self._handle_permission(permission_class.op1_class),
            ]

        return [
            self._handle_permission(permission_class),
        ]

    def _gather_permissions(self) -> List[PermissionItem]:
        items = []

        for permission_class in getattr(self.view, "permission_classes", []):
            items += self._handle_operation_holder(permission_class)

        return [i for i in items if i]

    def _get_permissions_description(self):
        permission_items = self._gather_permissions()

        if permission_items:
            return "\n\n**Permissions:**\n" + "\n".join(
                self._render_permission_item(item) for item in permission_items
            )
        else:
            return None

    def _render_permission_item(self, item):
        return f"+ `{item.name}`: *{item.doc_str}*"

    def _render_json(self, data):
        return f"<pre>{json.dumps(data, indent=4, sort_keys=True)}</pre>"

    def get_tags(self, operation_keys=None) -> List[AnyStr]:
        """
        Override method for rendering nested routers tags in GUI
        """
        tags = operation_keys[:-1]
        tags = map(lambda tag: tag.replace("_", " ").title(), tags)
        return [" > ".join(tags)]
