"""api.py: Relationship"""


import logging
import re

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.http.response import Http404
from django.urls import reverse
from rest_framework import serializers, viewsets
from rest_framework.response import Response

from axis.company.models import Company
from .messages import (
    RelationshipCreatedMessage,
    RelationshipDeletedMessage,
    RelationshipRejectedMessage,
    RelationshipRemovedMessage,
)
from .models import Relationship
from .utils import create_or_update_spanning_relationships

__author__ = "Autumn Valenta"
__date__ = "5/27/13 10:29 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]

log = logging.getLogger(__name__)


class RelationshipSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="company.name")
    company = serializers.HyperlinkedRelatedField(view_name="apiv2:company-detail", read_only=True)
    company_id = serializers.IntegerField(source="company.id")
    company_url = serializers.CharField(source="company.get_absolute_url", read_only=True)
    content_type = serializers.HyperlinkedRelatedField(
        view_name="apiv2:content_type-detail", read_only=True
    )
    content_object = serializers.SerializerMethodField()

    class Meta:
        model = Relationship
        fields = (
            "id",
            "company",
            "company_id",
            "company_url",
            "content_object",
            "content_type",
            "is_attached",
            "is_owned",
            "is_reportable",
            "is_viewable",
            "name",
            "object_id",
        )

    content_type_lookup_keys = {
        "company": "company",
        "Provider": "company",
        "eep organization": "company",
        "hvac organization": "company",
        "builder organization": "company",
        "utility organization": "company",
        "rater organization": "company",
        "qa organization": "company",
        "general organization": "company",
        "subdivision": "subdivision",
        "community": "community",
        "type": "type",
        "floorplan": "floorplan",
        "home": "home",
    }

    def get_content_object(self, obj):
        object_type = self.content_type_lookup_keys.get(obj.content_type.name)
        if object_type:
            return reverse("apiv2:{}-detail".format(object_type), kwargs={"pk": obj.id})

        return "'{}' not identifiable".format(obj.content_type.name)


class RelationshipViewSet(viewsets.ModelViewSet):
    # This viewset is actually ripped up into individual views in core/api_v2.py due to complicated
    # url design, so we're not using the normal @action stuff.
    # Would be nice if we got away from the specialized routing on this.
    model = Relationship
    queryset = model.objects.all()
    serializer_class = RelationshipSerializer

    def discover(self, request, **kwargs):
        """
        Using the provided data parameters see if an object exists and if it does whether the user
        has a relationship to that object
        Unless if you inputed the wrong stuff it should return a success.  What you do with the
        returned data ultimately determines the success / failure.
        /api/v2/relationship/discover/?format=json&app_label=community&model=community&name=Test2&city=22709&relationship__company=83
        """

        data = {
            "search_params": {"content_type": {}, "kwargs": {}},
            "object_exists": False,
            "relationships": [],
            "relationships_exist": False,
        }

        # NOTE: We're not supporting pagination here.  If you ask, you receive everything.

        builtin_defs = ["format", "page"]
        get_params = dict([x for x in request.query_params.items() if x[0] not in builtin_defs])

        if not {"app_label", "model"}.issubset(set(get_params.keys())):
            data = {"errors": "Missing required app_label and model"}
        else:
            content_type_kwargs = {
                "app_label": get_params.pop("app_label"),
                "model": get_params.pop("model"),
            }
            data["search_params"]["content_type"] = content_type_kwargs

            err_on_exists_no_rel = get_params.pop("error_on_objects_exists_and_no_relation", False)
            data["error_on_objects_exists_and_no_relation"] = err_on_exists_no_rel

            relationship_params = {}
            for k, v in get_params.items():
                m = re.match(r"relationship__(\w+)", k)
                if m and m.group(1) in [f.name for f in Relationship._meta.fields]:
                    # name = m.group(1) if m.group(1) != "company" else "company_id"
                    # value = v if m.group(1) != "company" else int(v)
                    # relationship_params[name] = value
                    relationship_params[m.group(1)] = v
                    del get_params[k]
            if len(relationship_params.keys()):
                data["search_params"]["relationship_params"] = relationship_params

            content_type = ContentType.objects.get(**content_type_kwargs)

            # All we need to look up are those keys which are unqiue
            _unique_fields = [f.name for f in content_type.model_class()._meta.fields if f.unique]
            search_args = [f for f in _unique_fields if f in get_params]
            if not len(search_args):
                for item in content_type.model_class()._meta.unique_together:
                    if set(item).issubset(get_params.keys()):
                        search_args += item
            search_args = list(set(search_args))
            data["search_params"]["kwargs"] = dict((k, get_params[k]) for k in search_args)

            data["object_exists"] = False
            try:
                object = content_type.get_object_for_this_type(**data["search_params"]["kwargs"])
                data["object_exists"] = True
            except ObjectDoesNotExist:
                pass
            except MultipleObjectsReturned:
                name = content_type.model_class()._meta.verbose_name.capitalize()
                data["errors"] = "Multiple {} objects returned for query".format(name)
            else:
                for candidate in object.relationships.all():
                    data["relationships"].append(RelationshipSerializer(candidate).data)

                results = Relationship.objects.filter(
                    content_type=content_type, object_id=object.id, **relationship_params
                )
                data["relationships_count"] = results.count()
                data["relationships_exist"] = bool(data["relationships_count"])
                if not data["relationships_exist"]:
                    reverse_kwargs = {
                        "model": content_type_kwargs["model"],
                        "app_label": content_type_kwargs["app_label"],
                        "object_id": object.id,
                    }
                    data["create_url"] = reverse("relationship:add_id", kwargs=reverse_kwargs)

                    data["create_string"] = (
                        "'{}' already exists; <a href=\"{}\">Click here</a> if you "
                        "would like to create an association to '{}'".format(
                            object, reverse("relationship:add_id", kwargs=reverse_kwargs), object
                        )
                    )
                    if err_on_exists_no_rel:
                        data["errors"] = "{} '{}' already exists.".format(
                            object._meta.verbose_name, object
                        )

        if "errors" in data.keys():
            return Response(data, status=400)
        return Response(data)

    def add(self, request, *args, **kwargs):
        model = kwargs.get("model")
        object_id = kwargs.get("object_id")
        app_label = kwargs.get("app_label")
        company = request.user.company
        if self.request.user.is_superuser and kwargs.get("company_id"):
            company = Company.objects.get(id=kwargs.get("company_id"))

        content_type = ContentType.objects.get(app_label=app_label, model=model)
        obj, create = Relationship.objects.get_or_create_direct(
            company=company, content_type=content_type, object_id=object_id
        )
        obj.is_attached = True
        obj.is_viewable = True
        obj.is_reportable = True
        obj.is_owned = True
        obj.save()

        target_object = content_type.get_object_for_this_type(pk=object_id)
        create_or_update_spanning_relationships(
            company, target_object, skip_implied=True, push_down=True
        )

        action = "Created" if create else "Updated"
        RelationshipCreatedMessage().send(
            context={
                "action": action,
                "company": str(Company.objects.get(id=company.id)),
                "relationship": str(target_object),
                "assigning_company": str(request.user.company),
            },
            company=Company.objects.get(id=company.id),
            url=target_object.get_absolute_url(),
        )

        msg = "{} relationship {}".format(action, obj)
        return Response(
            {"result": msg, "message": """<b style='color:green;'>{}</b>""".format(action)}
        )

    def reject(self, request, *args, **kwargs):
        model = kwargs.get("model")
        object_id = kwargs.get("object_id")
        app_label = kwargs.get("app_label")

        obj = self._get_object(request.user, app_label, model, object_id)
        obj.is_owned = True
        obj.is_attached = False
        obj.is_viewable = False
        obj.is_reportable = False
        obj.save()

        RelationshipRejectedMessage().send(
            context=dict(relationship=str(obj)),
            company=obj.company,
        )

        msg = "Relationship between {} has been rejected.".format(obj)
        return Response({"result": msg, "message": """<b style='color:red;'>Rejected</b>"""})

    def remove(self, request, *args, **kwargs):
        model = kwargs.get("model")
        object_id = kwargs.get("object_id")
        app_label = kwargs.get("app_label")

        obj = self._get_object(request.user, app_label, model, object_id)
        obj.is_owned = True
        obj.is_attached = True
        obj.is_viewable = False
        obj.is_reportable = False
        obj.save()

        target_object = obj.content_type.get_object_for_this_type(pk=obj.object_id)
        target_object.save()

        RelationshipRemovedMessage().send(
            context=dict(relationship=str(obj)),
            company_id=obj.company,
        )
        msg = "Relationship between {} has been removed.".format(obj)
        return Response({"result": msg, "message": """<b style='color:red;'>Removed</b>"""})

    def delete(self, request, *args, **kwargs):
        model = kwargs.get("model")
        object_id = kwargs.get("object_id")
        app_label = kwargs.get("app_label")

        user = request.user
        company = request.user.company
        if self.request.user.is_superuser and kwargs.get("company_id"):
            company = Company.objects.get(id=kwargs.get("company_id"))
            user = None

        if not request.user.is_superuser:
            msg = "Deleting of a relationship is left to admins."
            message = "<b style='color:red;'>Sorry. {}</b>".format(msg)
            return Response({"result": msg, "message": message})

        obj = self._get_object(user, app_label, model, object_id, company=company)
        obj.delete()
        object_id = obj.object_id

        target_object = obj.content_type.get_object_for_this_type(pk=object_id)
        target_object.save()

        RelationshipDeletedMessage().send(
            context={"company": str(obj.company), "object": str(obj.get_content_object())},
            company=obj.company,
        )

        msg = "Relationship between {} has been deleted.".format(obj)
        return Response({"result": msg, "message": """<b style='color:red;'>Deleted</b>"""})

    def _get_object(self, user, app_label, model, object_id, company=None):
        queryset = self.get_queryset()
        content_type = ContentType.objects.get(app_label=app_label, model=model)

        company = company if company else user.company
        queryset = queryset.filter(company=company, content_type=content_type, object_id=object_id)

        try:
            obj = queryset.get()
        except Relationship.DoesNotExist:
            if model != "company":
                raise Http404(
                    "No {}s found matching the query".format(queryset.model._meta.verbose_name)
                )
            model_obj = Company.objects.get(id=object_id)
            content_type = ContentType.objects.get_for_model(model_obj)
            queryset = self.get_queryset()
            queryset = queryset.filter(
                company=company, content_type=content_type, object_id=object_id
            )
            try:
                obj = queryset.get()
            except Relationship.DoesNotExist:
                raise Http404(
                    "No {}s found matching the query".format(queryset.model._meta.verbose_name)
                )

        return obj
