# Generated by Django 3.1.8 on 2021-04-16 10:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_fsm
import phonenumber_field.modelfields
import simple_history.models


class Migration(migrations.Migration):
    dependencies = [
        ("company", "0022_auto_20210115_1627"),
        ("eep_program", "0022_merge_20210401_1458"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("customer_hirl", "0148_auto_20210415_1309"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="hirlprojectregistration",
            options={
                "ordering": ["-id"],
                "verbose_name": "Project Registration",
                "verbose_name_plural": "Project Registrations",
            },
        ),
        migrations.RemoveField(
            model_name="hirlprojectregistration",
            name="multi_family_number_of_units",
        ),
        migrations.AddField(
            model_name="hirlproject",
            name="number_of_units",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="historicalhirlproject",
            name="number_of_units",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name="HistoricalHIRLProjectRegistration",
            fields=[
                (
                    "id",
                    models.IntegerField(
                        auto_created=True, blank=True, db_index=True, verbose_name="ID"
                    ),
                ),
                (
                    "project_type",
                    models.PositiveSmallIntegerField(
                        choices=[(1, "Single Family"), (2, "Multi Family")], default=1
                    ),
                ),
                (
                    "state",
                    django_fsm.FSMField(
                        choices=[
                            ("new", "New"),
                            ("pending", "Pending"),
                            ("active", "Active"),
                            ("rejected", "Rejected"),
                        ],
                        default="new",
                        max_length=50,
                    ),
                ),
                ("state_changed_at", models.DateTimeField(blank=True, editable=False)),
                ("state_change_reason", models.TextField(blank=True)),
                ("builder_first_name", models.CharField(blank=True, max_length=32, null=True)),
                ("builder_last_name", models.CharField(blank=True, max_length=32, null=True)),
                ("builder_email", models.EmailField(blank=True, max_length=254, null=True)),
                (
                    "builder_phone_number",
                    phonenumber_field.modelfields.PhoneNumberField(
                        blank=True, max_length=128, null=True, region=None
                    ),
                ),
                (
                    "name_to_be_listed_on_commercial_certificate",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("same", "Same Name as Residential Builder/Developer"),
                            ("same", "Different Name(s) - email gbverifications"),
                        ],
                        max_length=32,
                        null=True,
                    ),
                ),
                (
                    "multi_family_project_name",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                (
                    "multi_family_project_client",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("builder", "Builder/General Contractor"),
                            ("developer", "Developer"),
                            ("owner", "Owner"),
                        ],
                        max_length=100,
                        null=True,
                    ),
                ),
                ("multi_family_project_description", models.TextField(blank=True, null=True)),
                (
                    "multi_family_project_estimated_completion_date",
                    models.DateField(blank=True, null=True),
                ),
                ("multi_family_project_website_url", models.TextField(blank=True, null=True)),
                (
                    "building_will_include_non_residential_space",
                    models.BooleanField(
                        default=False,
                        null=True,
                        verbose_name="Building(s) will include non-residential space (retail/commercial) ?",
                    ),
                ),
                (
                    "seeking_hud_mortgage_insurance_premium_reduction",
                    models.BooleanField(
                        default=False,
                        null=True,
                        verbose_name="Seeking HUD Mortgage Insurance Premium Reduction?",
                    ),
                ),
                (
                    "seeking_fannie_mae_green_financing",
                    models.BooleanField(
                        default=False, null=True, verbose_name="Seeking Fannie Mae Green financing?"
                    ),
                ),
                (
                    "seeking_freddie_mac_green_financing",
                    models.BooleanField(
                        default=False,
                        null=True,
                        verbose_name="Seeking Freddie Mac Green financing?",
                    ),
                ),
                (
                    "intended_to_be_affordable_housing",
                    models.BooleanField(
                        default=False, null=True, verbose_name="Intended to be affordable housing?"
                    ),
                ),
                ("community_named_on_certificate", models.BooleanField(null=True)),
                (
                    "application_packet_completion",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("builder", "Builder"),
                            ("architect", "Architect"),
                            ("community_owner", "Owner"),
                            ("developer", "Developer"),
                        ],
                        default="builder",
                        max_length=255,
                        null=True,
                    ),
                ),
                (
                    "party_named_on_certificate",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("builder", "Builder"),
                            ("architect", "Architect"),
                            ("community_owner", "Owner"),
                            ("developer", "Developer"),
                        ],
                        default="builder",
                        max_length=255,
                        null=True,
                    ),
                ),
                (
                    "project_contact_first_name",
                    models.CharField(blank=True, max_length=32, null=True),
                ),
                (
                    "project_contact_last_name",
                    models.CharField(blank=True, max_length=32, null=True),
                ),
                ("project_contact_email", models.EmailField(blank=True, max_length=254, null=True)),
                (
                    "project_contact_phone_number",
                    phonenumber_field.modelfields.PhoneNumberField(
                        blank=True, max_length=128, null=True, region=None
                    ),
                ),
                ("developer_first_name", models.CharField(blank=True, max_length=255, null=True)),
                ("developer_last_name", models.CharField(blank=True, max_length=255, null=True)),
                ("developer_email", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "developer_phone",
                    phonenumber_field.modelfields.PhoneNumberField(
                        blank=True, max_length=128, null=True, region=None
                    ),
                ),
                ("owner_first_name", models.CharField(blank=True, max_length=255, null=True)),
                ("owner_last_name", models.CharField(blank=True, max_length=255, null=True)),
                ("owner_email", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "owner_phone",
                    phonenumber_field.modelfields.PhoneNumberField(
                        blank=True, max_length=128, null=True, region=None
                    ),
                ),
                ("architect_first_name", models.CharField(blank=True, max_length=255, null=True)),
                ("architect_last_name", models.CharField(blank=True, max_length=255, null=True)),
                ("architect_email", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "architect_phone",
                    phonenumber_field.modelfields.PhoneNumberField(
                        blank=True, max_length=128, null=True, region=None
                    ),
                ),
                ("marketing_first_name", models.CharField(blank=True, max_length=255, null=True)),
                ("marketing_last_name", models.CharField(blank=True, max_length=255, null=True)),
                ("marketing_email", models.EmailField(blank=True, max_length=254, null=True)),
                (
                    "marketing_phone",
                    phonenumber_field.modelfields.PhoneNumberField(
                        blank=True, max_length=128, null=True, region=None
                    ),
                ),
                (
                    "sales_phone",
                    phonenumber_field.modelfields.PhoneNumberField(
                        blank=True, max_length=128, null=True, region=None
                    ),
                ),
                ("sales_email", models.EmailField(blank=True, max_length=254, null=True)),
                ("sales_website_url", models.TextField(blank=True, null=True)),
                (
                    "entity_responsible_for_payment",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("builder", "Builder"),
                            ("architect", "Architect"),
                            ("community_owner", "Owner"),
                            ("developer", "Developer"),
                        ],
                        default="builder",
                        max_length=255,
                        null=True,
                    ),
                ),
                ("billing_first_name", models.CharField(blank=True, max_length=255, null=True)),
                ("billing_last_name", models.CharField(blank=True, max_length=255, null=True)),
                ("billing_email", models.EmailField(blank=True, max_length=254, null=True)),
                (
                    "billing_phone",
                    phonenumber_field.modelfields.PhoneNumberField(
                        blank=True, max_length=128, null=True, region=None
                    ),
                ),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_date", models.DateTimeField()),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                (
                    "history_type",
                    models.CharField(
                        choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")], max_length=1
                    ),
                ),
                (
                    "architect_organization",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="company.architectorganization",
                    ),
                ),
                (
                    "builder_organization",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="company.builderorganization",
                    ),
                ),
                (
                    "community_owner_organization",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="company.communityownerorganization",
                    ),
                ),
                (
                    "developer_organization",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="company.developerorganization",
                    ),
                ),
                (
                    "eep_program",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="eep_program.eepprogram",
                        verbose_name="Program",
                    ),
                ),
                (
                    "history_user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "registration_user",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "historical Project Registration",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": "history_date",
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]
