""" Core testing utilties for axis. """

__author__ = "Autumn Valenta"
__date__ = "07-11-14 12:14 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

import logging
from io import BytesIO
from PIL import Image
from collections import OrderedDict

log = logging.getLogger(__name__)


# Helpful for passing a subset of items from a "**kwargs" dict to sub-factories.
def subdict_from_prefix(d, prefix, extra=None, remove_prefix=True):
    """Includes items from ``d`` if they begin with ``prefix``.  Result dict strips prefix."""
    extra = {} if extra is None else extra
    prefix_length = len(prefix)
    data = {
        (k[prefix_length:] if remove_prefix else k): v for k, v in d.items() if k.startswith(prefix)
    }
    data.update(extra)
    return data


def create_test_image(width=50, height=50):
    """
    Generate random image for testing

    Example usage with Django model:

    from django.core.files.uploadedfile import SimpleUploadedFile
    SimpleUploadedFile(
            'test.png',
            create_test_image().read()
        )
    :return: file
    """
    file = BytesIO()
    image = Image.new("RGBA", size=(width, height), color=(155, 0, 0))
    image.save(file, "png")
    file.name = "test.png"
    file.seek(0)
    return file
