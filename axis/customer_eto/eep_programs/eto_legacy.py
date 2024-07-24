__author__ = "Autumn Valenta"
__date__ = "10/08/18 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]
import logging

from axis.eep_program.program_builder.base import ProgramCloner

log = logging.getLogger(__name__)


class Eto2018(ProgramCloner):
    base_program = "eto-2018"
    slug = "eto-2018"
    qa_slug = "eto-2018-qa"
    qa_name = "Energy Trust Oregon - 2018 QA"
    convert_to_collection = True


class Eto2017(ProgramCloner):
    base_program = "eto-2017"
    slug = "eto-2017"
    qa_slug = "eto-2017-qa"
    qa_name = "Energy Trust Oregon - 2017 QA"
    convert_to_collection = True


class Eto2016(ProgramCloner):
    base_program = "eto-2016"
    slug = "eto-2016"
    qa_slug = "eto-2016-qa"
    qa_name = "Energy Trust Oregon - 2016 QA"
    convert_to_collection = True


class Eto2015(ProgramCloner):
    base_program = "eto-2015"
    slug = "eto-2015"
    convert_to_collection = True


class Eto2014(ProgramCloner):
    base_program = "eto"
    slug = "eto"
    convert_to_collection = True
