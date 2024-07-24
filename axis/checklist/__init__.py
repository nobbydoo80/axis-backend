"""__init__.py: Django checklist package container"""


import os


__author__ = "Gaurav Kapoor"
__version__ = "78.0.6"
__version_info__ = (78, 0, 6)
__date__ = "2012/1/30 1:18:00 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions.Consulting. All rights reserved."
__credits__ = ["Steven Klass", "Eric Walker", "Autumn Valenta", "Michael Jeffrey"]
__license__ = "See the file LICENSE.txt for licensing information."

MASTER_BULK_TEMPLATE = os.path.abspath(
    os.path.dirname(__file__) + "/static/templates/Checklist_Master_Template.xlsx"
)
