__author__ = "Autumn Valenta"
__date__ = "2019-05-16 4:47 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = ["Autumn Valenta"]

from axis.company import api
from .router import api_router


api_router.register(r"company/eep_programs", api.CompanyEEPProgramViewSet, "company_eep_programs")
