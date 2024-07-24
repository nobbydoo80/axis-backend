#!/usr/bin/env python

import os
import sys

from django.core.management import execute_from_command_line

from settings.env import env


# Linux / Mac
for dir_name, _dn, _fn in os.walk("lib"):
    if len(dir_name.split("/")) == 2:
        sys.path.append(os.path.abspath(dir_name))

# Windows...
for dir_name, _dn, _fn in os.walk("src"):
    if len(dir_name.split("\\")) == 2:
        sys.path.append(os.path.abspath(dir_name))

if __name__ == "__main__":
    execute_from_command_line(argv=sys.argv[0:])
