# Generated by Django 1.11.16 on 2018-10-08 18:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("annotation", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="historicalannotation",
            name="history_user",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="historicalannotation",
            name="type",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="annotation.Type",
            ),
        ),
        migrations.AddField(
            model_name="historicalannotation",
            name="user",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="annotation",
            name="content_type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="contenttypes.ContentType"
            ),
        ),
        migrations.AddField(
            model_name="annotation",
            name="type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="annotation.Type",
                verbose_name="Annotation Type",
            ),
        ),
        migrations.AddField(
            model_name="annotation",
            name="user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
