# Generated by Django 1.11.26 on 2020-01-13 16:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("scheduling", "0006_auto_20200113_1130"),
    ]

    operations = [
        migrations.AddField(
            model_name="historicaltask",
            name="approver",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Approver",
            ),
        ),
        migrations.AddField(
            model_name="task",
            name="approver",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
                verbose_name="Approver",
            ),
        ),
    ]