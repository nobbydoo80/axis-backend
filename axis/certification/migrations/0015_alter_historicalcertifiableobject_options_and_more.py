# Generated by Django 4.0.7 on 2022-09-15 17:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_states.fields


class Migration(migrations.Migration):
    dependencies = [
        ("company", "0030_alter_company_city_alter_company_group_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("certification", "0014_auto_20201230_1218"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="historicalcertifiableobject",
            options={
                "get_latest_by": ("history_date", "history_id"),
                "ordering": ("-history_date", "-history_id"),
                "verbose_name": "historical Certifiable Object",
                "verbose_name_plural": "historical Certifiable Objects",
            },
        ),
        migrations.AlterModelOptions(
            name="historicalworkflowstatus",
            options={
                "get_latest_by": ("history_date", "history_id"),
                "ordering": ("-history_date", "-history_id"),
                "verbose_name": "historical workflow status",
                "verbose_name_plural": "historical Workflow Statuses",
            },
        ),
        migrations.AlterField(
            model_name="historicalcertifiableobject",
            name="history_date",
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name="historicalcertifiableobject",
            name="id",
            field=models.BigIntegerField(
                auto_created=True, blank=True, db_index=True, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="historicalworkflowstatus",
            name="history_date",
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name="historicalworkflowstatus",
            name="id",
            field=models.BigIntegerField(
                auto_created=True, blank=True, db_index=True, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="historicalworkflowstatusstatelog",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="historicalworkflowstatusstatelog",
            name="state",
            field=django_states.fields.StateField(
                default="transition_initiated", max_length=100, verbose_name="state id"
            ),
        ),
        migrations.AlterField(
            model_name="trcprojectdata",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="trcprojectsettings",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="workflow",
            name="config_path",
            field=models.FilePathField(
                allow_folders=True,
                match="^[^_].*(?<!\\.pyc)$",
                path="/home/pivotal/axis/certification/configs",
            ),
        ),
        migrations.AlterField(
            model_name="workflowstatus",
            name="certifiable_object",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="certification.certifiableobject",
            ),
        ),
        migrations.AlterField(
            model_name="workflowstatusassociation",
            name="company",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="%(class)s",
                to="company.company",
            ),
        ),
        migrations.AlterField(
            model_name="workflowstatusassociation",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="workflowstatusassociation",
            name="owner",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="owned_%(class)s_associations",
                to="company.company",
            ),
        ),
        migrations.AlterField(
            model_name="workflowstatusassociation",
            name="user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="%(class)s",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="workflowstatusstatelog",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="workflowstatusstatelog",
            name="state",
            field=django_states.fields.StateField(
                default="transition_initiated", max_length=100, verbose_name="state id"
            ),
        ),
    ]