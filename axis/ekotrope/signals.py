import logging

from django.db.models.signals import post_save

from .tasks import import_project_tree

__author__ = "Autumn Valenta"
__date__ = "10/31/16 09:02"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


def register_signals():
    """Nested to avoid tangling import during initial load."""

    # log.debug("Registering late signals.")

    from axis.floorplan.models import Floorplan

    post_save.connect(fetch_full_object, sender=Floorplan)


# sender=Floorplan
def fetch_full_object(sender, instance, **kwargs):
    if kwargs.get("raw"):
        return

    from .models import EkotropeAuthDetails

    if instance.ekotrope_houseplan:
        # We're trigging a full import if there's a houseplan set so that changes on the
        # Ekotrope side can be observed.

        project = instance.ekotrope_houseplan.project
        auth_details = EkotropeAuthDetails.objects.filter(user__company=project.company).first()
        if auth_details:
            import_project_tree.delay(auth_details.id, project.id)
        else:
            msg = "No creds found for Ekotrope project %(project)s owned by %(company)s (%(co_id)s)"
            log.error(
                msg
                % {
                    "project": project.id,
                    "company": str(project.company),
                    "co_id": project.company.id,
                }
            )
