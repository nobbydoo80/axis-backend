import logging
import os
import tempfile
import time

from django.conf import settings
from django.core.files.storage import default_storage

__author__ = "Steven Klass"
__date__ = "5/28/12 7:56 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


def get_physical_file(document, log=None, counter=100, quiet=False):
    only_object = False if log is None else True
    log = log if log else logging.getLogger(__name__)

    errors, warnings, info = [], [], []
    if document is None:
        raise IOError("No Document passed")

    filename = os.path.join(settings.MEDIA_ROOT, document)
    if not os.path.isfile(filename):
        s3_file = None
        while True:
            try:
                s3_file = default_storage.open(document, "rb")
                break
            except IOError:
                if counter == 0:
                    if not quiet:
                        log.exception("Unable to open %(file)s", {"file": document})
                    raise
                counter -= 1
                time.sleep(5)
        if s3_file:
            file_format = os.path.splitext(filename)[-1].lower()
            new_filename = tempfile.NamedTemporaryFile(delete=False, suffix=file_format)
            new_filename.write(s3_file.read())
            new_filename.close()
            log.debug("Creating local copy of %s to %s", document, new_filename.name)
            if only_object:
                return new_filename.name
            return new_filename.name, (errors, warnings, info)
    else:
        if only_object:
            return filename
        else:
            return filename, (errors, warnings, info)

    log.error("No file found to open %(file)s", {"file": document}, exc_info=1)

    if only_object:
        return None

    return None, ("No File", warnings, info)
