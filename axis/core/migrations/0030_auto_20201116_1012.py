# Generated by Django 2.2 on 2020-11-16 10:12
import datetime

import dateutil.parser
from django.utils import timezone
from django.db import migrations, models


def forward(apps, schema_editor):
    """This will update all users"""

    FlatPage = apps.get_model("flatpages", "FlatPage")
    AxisFlatPage = apps.get_model("core", "AxisFlatPage")
    flatpages = FlatPage.objects.all()
    for flatpage in flatpages:
        if not getattr(flatpage, "axisflatpage", None):
            fields = [f.name for f in FlatPage._meta.fields if f.name != "id"]
            values = dict([(x, getattr(flatpage, x)) for x in fields])
            axis_flat_page = AxisFlatPage(flatpage_ptr=flatpage, order=0, **values)

            try:
                axis_flat_page.created_at = dateutil.parser.parse(
                    flatpage.url.split("/")[2]
                ).replace(tzinfo=datetime.timezone.utc)
            except ValueError:
                axis_flat_page.created_at = timezone.now()
            axis_flat_page.save()


def backward(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0029_auto_20201116_1010"),
    ]

    operations = [
        migrations.AlterField(
            model_name="axisflatpage",
            name="created_at",
            field=models.DateTimeField(
                default=timezone.now,
                editable=True,
                blank=True,
                help_text="This field is using for "
                "ordering FlatPages. "
                "For example: News list",
            ),
        ),
        migrations.RunPython(forward, backward),
    ]
