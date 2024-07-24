"""Menu API"""


from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from ...context_processors import menu

__author__ = "Artem Hruzd"
__date__ = "01/06/2020 19:50"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class MenuAPIView(APIView):
    permission_classes = [AllowAny]  # Public menu is served from here
    throttle_classes = ()

    def get(self, request, **kwargs):
        data = menu(request)
        for i, item in enumerate(data["menu"]):
            if hasattr(item, "as_dict"):
                data["menu"][i] = item.as_dict()
        return Response(data)
