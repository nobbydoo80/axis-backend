from axis.customer_eto import api
from ..router import api_router

__author__ = "Autumn Valenta"
__date__ = "2019-05-16 4:47 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = ["Autumn Valenta"]


api_router.register(r"eto_account", api.ETOAccountViewSet, "eto_account")
api_router.register(r"projecttracking", api.FastTrackSubmissionViewSet, "fasttrack")

# legacy url from apiv1, before they renamed their service
api_router.register(r"fasttrack/project", api.FastTrackSubmissionViewSet)
