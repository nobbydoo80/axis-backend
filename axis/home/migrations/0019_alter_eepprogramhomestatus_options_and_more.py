# Generated by Django 4.0.7 on 2022-09-14 19:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_states.fields


class Migration(migrations.Migration):
    dependencies = [
        ("geographic", "0006_auto_20220719_1459"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("eep_program", "0023_auto_20220720_2313"),
        ("company", "0030_alter_company_city_alter_company_group_and_more"),
        ("subdivision", "0009_alter_historicalsubdivision_builder_org_and_more"),
        ("home", "0018_auto_20210426_1358"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="eepprogramhomestatus",
            options={"verbose_name": "Project Status", "verbose_name_plural": "Project Statuses"},
        ),
        migrations.AlterModelOptions(
            name="eepprogramhomestatusstatelog",
            options={"verbose_name": "Project Status transition"},
        ),
        migrations.AlterModelOptions(
            name="historicaleepprogramhomestatus",
            options={"ordering": ("-history_date",), "verbose_name": "Historical Project"},
        ),
        migrations.AlterModelOptions(
            name="historicaleepprogramhomestatusstatelog",
            options={"verbose_name": "Historical Project transition"},
        ),
        migrations.AlterModelOptions(
            name="historicalhome",
            options={
                "get_latest_by": ("history_date", "history_id"),
                "ordering": ("-history_date", "-history_id"),
                "verbose_name": "historical Project",
                "verbose_name_plural": "historical Projects",
            },
        ),
        migrations.AlterModelOptions(
            name="home",
            options={"verbose_name": "Project", "verbose_name_plural": "Projects"},
        ),
        migrations.AlterField(
            model_name="eepprogramhomestatus",
            name="eep_program",
            field=models.ForeignKey(
                help_text="Select the program from the list presented. You may add multiple programs to a project using the 'Add new program' button below. You may customize the list of programs presented on the Tasks -> Programs page.",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="homestatuses",
                to="eep_program.eepprogram",
                verbose_name="Program",
            ),
        ),
        migrations.AlterField(
            model_name="eepprogramhomestatus",
            name="state",
            field=django_states.fields.StateField(
                default="pending_inspection", max_length=100, verbose_name="state id"
            ),
        ),
        migrations.AlterField(
            model_name="eepprogramhomestatusassociation",
            name="company",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="%(class)s",
                to="company.company",
            ),
        ),
        migrations.AlterField(
            model_name="eepprogramhomestatusassociation",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="eepprogramhomestatusassociation",
            name="owner",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="owned_%(class)s_associations",
                to="company.company",
            ),
        ),
        migrations.AlterField(
            model_name="eepprogramhomestatusassociation",
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
            model_name="eepprogramhomestatusstatelog",
            name="from_state",
            field=models.CharField(
                choices=[
                    ("pending_inspection", "Pending"),
                    ("inspection", "Active"),
                    ("qa_pending", "Pending QA"),
                    ("certification_pending", "Inspected"),
                    ("complete", "Certified"),
                    ("failed", "Failed"),
                    ("abandoned", "Abandoned"),
                    ("customer_hirl_pending_project_data", "Pending Project Data"),
                    ("customer_hirl_pending_rough_qa", "Pending Rough QA"),
                    ("customer_hirl_pending_final_qa", "Pending Final QA"),
                ],
                max_length=100,
            ),
        ),
        migrations.AlterField(
            model_name="eepprogramhomestatusstatelog",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="eepprogramhomestatusstatelog",
            name="state",
            field=django_states.fields.StateField(
                default="transition_initiated", max_length=100, verbose_name="state id"
            ),
        ),
        migrations.AlterField(
            model_name="eepprogramhomestatusstatelog",
            name="to_state",
            field=models.CharField(
                choices=[
                    ("pending_inspection", "Pending"),
                    ("inspection", "Active"),
                    ("qa_pending", "Pending QA"),
                    ("certification_pending", "Inspected"),
                    ("complete", "Certified"),
                    ("failed", "Failed"),
                    ("abandoned", "Abandoned"),
                    ("customer_hirl_pending_project_data", "Pending Project Data"),
                    ("customer_hirl_pending_rough_qa", "Pending Rough QA"),
                    ("customer_hirl_pending_final_qa", "Pending Final QA"),
                ],
                max_length=100,
            ),
        ),
        migrations.AlterField(
            model_name="historicaleepprogramhomestatus",
            name="eep_program",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                help_text="Select the program from the list presented. You may add multiple programs to a project using the 'Add new program' button below. You may customize the list of programs presented on the Tasks -> Programs page.",
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="eep_program.eepprogram",
                verbose_name="Program",
            ),
        ),
        migrations.AlterField(
            model_name="historicaleepprogramhomestatus",
            name="history_date",
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name="historicaleepprogramhomestatus",
            name="id",
            field=models.BigIntegerField(
                auto_created=True, blank=True, db_index=True, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="historicaleepprogramhomestatus",
            name="state",
            field=django_states.fields.StateField(
                default="pending_inspection", max_length=100, verbose_name="state id"
            ),
        ),
        migrations.AlterField(
            model_name="historicaleepprogramhomestatusstatelog",
            name="from_state",
            field=models.CharField(
                choices=[
                    ("pending_inspection", "Pending"),
                    ("inspection", "Active"),
                    ("qa_pending", "Pending QA"),
                    ("certification_pending", "Inspected"),
                    ("complete", "Certified"),
                    ("failed", "Failed"),
                    ("abandoned", "Abandoned"),
                    ("customer_hirl_pending_project_data", "Pending Project Data"),
                    ("customer_hirl_pending_rough_qa", "Pending Rough QA"),
                    ("customer_hirl_pending_final_qa", "Pending Final QA"),
                ],
                max_length=100,
            ),
        ),
        migrations.AlterField(
            model_name="historicaleepprogramhomestatusstatelog",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="historicaleepprogramhomestatusstatelog",
            name="state",
            field=django_states.fields.StateField(
                default="transition_initiated", max_length=100, verbose_name="state id"
            ),
        ),
        migrations.AlterField(
            model_name="historicaleepprogramhomestatusstatelog",
            name="to_state",
            field=models.CharField(
                choices=[
                    ("pending_inspection", "Pending"),
                    ("inspection", "Active"),
                    ("qa_pending", "Pending QA"),
                    ("certification_pending", "Inspected"),
                    ("complete", "Certified"),
                    ("failed", "Failed"),
                    ("abandoned", "Abandoned"),
                    ("customer_hirl_pending_project_data", "Pending Project Data"),
                    ("customer_hirl_pending_rough_qa", "Pending Rough QA"),
                    ("customer_hirl_pending_final_qa", "Pending Final QA"),
                ],
                max_length=100,
            ),
        ),
        migrations.AlterField(
            model_name="historicalhome",
            name="city",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                help_text='Type the first few letters of the name of the city the project is located in and select the correct city/state/county combination from the list presented. If the correct city is not available, click "Add New" to add a city to the database.',
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="geographic.city",
                verbose_name="City",
            ),
        ),
        migrations.AlterField(
            model_name="historicalhome",
            name="history_date",
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name="historicalhome",
            name="id",
            field=models.BigIntegerField(
                auto_created=True, blank=True, db_index=True, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="historicalhome",
            name="lot_number",
            field=models.CharField(
                blank=True,
                help_text='Enter the lot number of the project (typical for a "production builder" in a subdivision or development of multiple projects), or leave blank or "N/A" if unknown or not applicable.',
                max_length=16,
                null=True,
                verbose_name="Lot number",
            ),
        ),
        migrations.AlterField(
            model_name="historicalhome",
            name="street_line1",
            field=models.CharField(
                blank=True,
                help_text="Enter the street number and street name of the project (e.g. 123 Main St).",
                max_length=100,
                null=True,
                verbose_name="Street Address",
            ),
        ),
        migrations.AlterField(
            model_name="historicalhome",
            name="subdivision",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="subdivision.subdivision",
                verbose_name="Subdivision/MF Development",
            ),
        ),
        migrations.AlterField(
            model_name="historicalhome",
            name="zipcode",
            field=models.CharField(
                blank=True,
                help_text="Enter the 5-digit ZIP Code of project.",
                max_length=15,
                null=True,
                verbose_name="ZIP Code",
            ),
        ),
        migrations.AlterField(
            model_name="home",
            name="city",
            field=models.ForeignKey(
                blank=True,
                help_text='Type the first few letters of the name of the city the project is located in and select the correct city/state/county combination from the list presented. If the correct city is not available, click "Add New" to add a city to the database.',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="geographic.city",
                verbose_name="City",
            ),
        ),
        migrations.AlterField(
            model_name="home",
            name="lot_number",
            field=models.CharField(
                blank=True,
                help_text='Enter the lot number of the project (typical for a "production builder" in a subdivision or development of multiple projects), or leave blank or "N/A" if unknown or not applicable.',
                max_length=16,
                null=True,
                verbose_name="Lot number",
            ),
        ),
        migrations.AlterField(
            model_name="home",
            name="place",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="%(class)s_set",
                to="geographic.place",
            ),
        ),
        migrations.AlterField(
            model_name="home",
            name="street_line1",
            field=models.CharField(
                blank=True,
                help_text="Enter the street number and street name of the project (e.g. 123 Main St).",
                max_length=100,
                null=True,
                verbose_name="Street Address",
            ),
        ),
        migrations.AlterField(
            model_name="home",
            name="subdivision",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="subdivision.subdivision",
                verbose_name="Subdivision/MF Development",
            ),
        ),
        migrations.AlterField(
            model_name="home",
            name="zipcode",
            field=models.CharField(
                blank=True,
                help_text="Enter the 5-digit ZIP Code of project.",
                max_length=15,
                null=True,
                verbose_name="ZIP Code",
            ),
        ),
        migrations.AlterField(
            model_name="homephoto",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="standarddisclosuresettings",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
    ]
