"""managers.py: Django resnet"""

import logging

from django.db import models

__author__ = "Steven Klass"
__date__ = "7/25/14 5:18 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class RESNETContactManager(models.Manager):
    def update_or_create(self, **kwargs):
        kwrgs = {"name": kwargs.pop("name"), "resnet_company": kwargs.pop("resnet_company")}

        kwargs["is_active"] = True

        try:
            obj = self.model.objects.get(**kwrgs)
            for key, value in kwargs.items():
                setattr(obj, key, value)
        except self.model.DoesNotExist:
            kwargs.update(**kwrgs)
            obj = self.model(**kwargs)
        except self.model.MultipleObjectsReturned:
            err = "Multiple Users found for {name} in {resnet_company}"
            log.error(err.format(**kwrgs), exc_info=1, extra=kwargs)
            raise

        obj.save()
        return obj


class RESNETCompanyManager(models.Manager):
    def update_or_create(self, **kwargs):
        kwrgs = {"name": kwargs.pop("name"), "state": kwargs.pop("state")}

        kwargs["is_active"] = True

        save_required = False
        try:
            obj = self.model.objects.get(**kwrgs)
            for key, value in kwargs.items():
                if getattr(obj, key) != value:
                    save_required = True
                    setattr(obj, key, value)
        except self.model.DoesNotExist:
            kwargs.update(**kwrgs)
            obj = self.model(**kwargs)
            save_required = True
        except self.model.MultipleObjectsReturned:
            msg = "Multiple Companies found for %(name)s in %(state)s"
            log.error(msg, *kwargs, exc_info=1)
            raise
        if save_required:
            obj.save()
        return obj
