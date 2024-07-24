"""message.py: """


from django_filters import rest_framework as filters

from axis.messaging.models import Message

__author__ = "Artem Hruzd"
__date__ = "01/07/2020 12:33"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]


class MessageFilter(filters.FilterSet):
    ALERTS_DELIVERY_TYPE = 0
    ALERTS_ONLY_DELIVERY_TYPE = 1
    EMAIL_DELIVERY_TYPE = 2

    DELIVERY_TYPE_CHOICES = (
        (ALERTS_DELIVERY_TYPE, "In-system alerts"),
        (ALERTS_ONLY_DELIVERY_TYPE, "In-system-only alerts"),
        (EMAIL_DELIVERY_TYPE, "Emailed notifications"),
    )

    category = filters.CharFilter(
        field_name="category", help_text="All available Message Categories for user. "
    )

    date_created__gt = filters.DateFilter(
        field_name="date_created", lookup_expr="gt", label="Date Created is greater then"
    )
    date_created__lt = filters.DateFilter(
        field_name="date_created", lookup_expr="lt", label="Date Created is less than"
    )
    date_created__range = filters.DateRangeFilter(
        field_name="date_created", label="Date Created range"
    )

    date_email_sent__gt = filters.DateFilter(
        field_name="date_sent", lookup_expr="gt", label="Date Emailed is greater then"
    )
    date_email_sent__lt = filters.DateFilter(
        field_name="date_sent", lookup_expr="lt", label="Date Emailed is less then"
    )
    date_email_sent__range = filters.DateRangeFilter(
        field_name="date_sent", label="Date Emailed range"
    )

    date_alerted__gt = filters.DateFilter(
        field_name="date_alerted", lookup_expr="gt", label="Date Alerted is less then"
    )
    date_alerted__lt = filters.DateFilter(
        field_name="date_alerted", lookup_expr="lt", label="Date Alerted is less then"
    )
    date_alerted__range = filters.DateRangeFilter(field_name="date_alerted")

    delivery_type = filters.ChoiceFilter(
        choices=DELIVERY_TYPE_CHOICES, method="filter_delivery_type", label="Delivery type"
    )

    class Meta:
        model = Message
        fields = ["level", "email_read", "alert_read"]

    def filter_delivery_type(self, queryset, name, value):
        if value == MessageFilter.ALERTS_DELIVERY_TYPE:
            queryset = queryset.exclude(date_alerted=None)
        elif value == MessageFilter.ALERTS_ONLY_DELIVERY_TYPE:
            queryset = queryset.exclude(date_alerted=None).filter(date_sent=None)
        elif value == MessageFilter.EMAIL_DELIVERY_TYPE:
            queryset = queryset.exclude(date_sent=None)
        return queryset
