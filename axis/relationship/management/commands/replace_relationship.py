from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

from axis.company.models import Company
from axis.home.models import Home
from axis.relationship.utils import replace_relationship_on_obj

import logging

__author__ = "Michael Jeffrey"
__date__ = "3/24/17 1:34 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Michael Jeffrey",
]


log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Replace a relationship of an entity with a Company of the same type."

    option_list = BaseCommand.option_list + (
        make_option(
            "--model",
            "-m",
            dest="model",
            type="string",
            help="Model Type to do the replace against",
        ),
        make_option(
            "--model-id",
            "-i",
            dest="model_id",
            type="int",
            help="Object ID to do the replace against",
        ),
        make_option("--remove", "-r", dest="replace", type="int", help="ID of company to remove"),
        make_option("--add", "-a", dest="replace_with", type="int", help="ID of company to add"),
        make_option(
            "--multiple",
            action="store_true",
            default=False,
            help="Process the replacement for multiple objects",
        ),
        make_option(
            "--force",
            action="store_true",
            default=False,
            help="Continue processing even if an object doesn't have an expected relationship",
        ),
    )

    supported_models = {"home": Home}

    def get_model(self, model_name):
        try:
            return self.supported_models[model_name]
        except KeyError:
            raise CommandError("Model {} is not supported yet.".format(model_name))

    def handle(self, *args, **options):
        model_name = options["model"]
        model_id = options["model_id"]
        replace_id = options["replace"]
        replace_with_id = options["replace_with"]
        force = options["force"]

        if not all([model_name, model_id, replace_id, replace_with_id]):
            raise CommandError(
                "All arguments must be provided: `-m {} -r {} -a {}`".format(
                    model_name, replace_id, replace_with_id
                )
            )

        Model = self.get_model(model_name)
        replace = Company.objects.get(id=replace_id)
        replace_with = Company.objects.get(id=replace_with_id)

        if options["multiple"]:
            instance_ids = map(int, args) + [options["model_id"]]
            if len(instance_ids) == 1:
                raise CommandError(
                    "Do not pass the --multiple flag if you are only processing one item."
                )

            self.handle_multiple(Model, instance_ids, replace, replace_with, force)
        else:
            if len(args) > 0:
                raise CommandError(
                    "Pass the --multiple flag if you are processing more than one item."
                )

            self.handle_single(Model, model_id, replace, replace_with, force)

    def handle_single(self, Model, instance_id, replace, replace_with, force):
        try:
            instance = Model.objects.get(id=instance_id)
        except Model.DoesNotExist:
            log.error("%s with id %s does not exist", Model, instance_id)
            if not force:
                raise  # do not continue
        else:
            replace_relationship_on_obj(instance, replace, replace_with, force)

    def handle_multiple(self, Model, instance_ids, replace, replace_with, force):
        for instance_id in instance_ids:
            self.handle_single(Model, instance_id, replace, replace_with, force)
