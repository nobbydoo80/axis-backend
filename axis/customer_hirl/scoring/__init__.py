__author__ = "Artem Hruzd"
__date__ = "06/19/2020 17:34"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


from axis.core.utils.registry import Registry
from .base import BaseScoringExtraction
from .new_construction_2020 import NewConstruction2020ScoringExtraction
from .new_construction_2015 import NewConstruction2015ScoringExtraction
from .certified_2020 import Certified2020ScoringExtraction
from .whole_house_remodel_2015 import WholeHouseRemodel2015ScoringExtraction
from .whole_house_remodel_2020 import WholeHouseRemodel2020ScoringExtraction
from .new_construction_2012 import NewConstruction2012ScoringExtraction
from .whole_house_remodel_2012 import WholeHouseRemodel2012ScoringExtraction
from .wri_2021 import WRI2021ScoringExtraction
from .land_development_2020 import LandDevelopment2020ScoringExtraction


# register all available Scoring Upload Parsers
scoring_registry = Registry()
scoring_registry.register(NewConstruction2020ScoringExtraction)
scoring_registry.register(WholeHouseRemodel2020ScoringExtraction)
scoring_registry.register(Certified2020ScoringExtraction)
scoring_registry.register(NewConstruction2015ScoringExtraction)
scoring_registry.register(WholeHouseRemodel2015ScoringExtraction)
scoring_registry.register(NewConstruction2012ScoringExtraction)
scoring_registry.register(WholeHouseRemodel2012ScoringExtraction)
scoring_registry.register(WRI2021ScoringExtraction)
scoring_registry.register(LandDevelopment2020ScoringExtraction)
