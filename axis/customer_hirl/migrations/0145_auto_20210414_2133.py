# Generated by Django 3.1.8 on 2021-04-14 21:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_fsm
import phonenumber_field.modelfields


class Migration(migrations.Migration):
    dependencies = [
        ("company", "0022_auto_20210115_1627"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("customer_hirl", "0144_auto_20210413_1223"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="hirlproject",
            name="application_packet_completion",
        ),
        migrations.RemoveField(
            model_name="hirlproject",
            name="architect_email",
        ),
        migrations.RemoveField(
            model_name="hirlproject",
            name="architect_first_name",
        ),
        migrations.RemoveField(
            model_name="hirlproject",
            name="architect_last_name",
        ),
        migrations.RemoveField(
            model_name="hirlproject",
            name="architect_organization",
        ),
        migrations.RemoveField(
            model_name="hirlproject",
            name="architect_phone",
        ),
        migrations.RemoveField(
            model_name="hirlproject",
            name="billing_email",
        ),
        migrations.RemoveField(
            model_name="hirlproject",
            name="billing_first_name",
        ),
        migrations.RemoveField(
            model_name="hirlproject",
            name="billing_last_name",
        ),
        migrations.RemoveField(
            model_name="hirlproject",
            name="billing_phone",
        ),
        migrations.RemoveField(
            model_name="hirlproject",
            name="builder_email",
        ),
        migrations.RemoveField(
            model_name="hirlproject",
            name="builder_first_name",
        ),
        migrations.RemoveField(
            model_name="hirlproject",
            name="builder_last_name",
        ),
        migrations.RemoveField(
            model_name="hirlproject",
            name="builder_organization",
        ),
        migrations.RemoveField(
            model_name="hirlproject",
            name="builder_phone_number",
        ),
        migrations.RemoveField(
            model_name="hirlproject",
            name="building_will_include_non_residential_space",
        ),
        migrations.RemoveField(
            model_name="hirlproject",
            name="community_named_on_certificate",
        ),
        migrations.RemoveField(
            model_name="hirlproject",
            name="community_owner_organization",
        ),
        migrations.RemoveField(
            model_name="hirlproject",
            name="developer_email",
        ),
        migrations.RemoveField(
            model_name="hirlproject",
            name="developer_first_name",
        ),
        migrations.RemoveField(
            model_name="hirlproject",
            name="developer_last_name",
        ),
        migrations.RemoveField(
            model_name="hirlproject",
            name="developer_organization",
        ),
        migrations.RemoveField(
            model_name="hirlproject",
            name="developer_phone",
        ),
        migrations.RemoveField(
            model_name="hirlproject",
            name="entity_responsible_for_payment",
        ),
        migrations.RemoveField(
            model_name="hirlproject",
            name="intended_to_be_affordable_housing",
        ),
        migrations.RemoveField(
            model_name="hirlproject",
            name="marketing_email",
        ),
        migrations.RemoveField(
            model_name="hirlproject",
            name="marketing_first_name",
        ),
        migrations.RemoveField(
            model_name="hirlproject",
            name="marketing_last_name",
        ),
        migrations.RemoveField(
            model_name="hirlproject",
            name="marketing_phone",
        ),
        migrations.RemoveField(
            model_name="hirlproject",
            name="multi_family_number_of_units",
        ),
        migrations.RemoveField(
            model_name="hirlproject",
            name="multi_family_project_client",
        ),
        migrations.RemoveField(
            model_name="hirlproject",
            name="multi_family_project_description",
        ),
        migrations.RemoveField(
            model_name="hirlproject",
            name="multi_family_project_estimated_completion_date",
        ),
        migrations.RemoveField(
            model_name="hirlproject",
            name="multi_family_project_name",
        ),
        migrations.RemoveField(
            model_name="hirlproject",
            name="multi_family_project_website_url",
        ),
        migrations.RemoveField(
            model_name="hirlproject",
            name="name_to_be_listed_on_commercial_certificate",
        ),
        migrations.RemoveField(
            model_name="hirlproject",
            name="owner_email",
        ),
        migrations.RemoveField(
            model_name="hirlproject",
            name="owner_first_name",
        ),
        migrations.RemoveField(
            model_name="hirlproject",
            name="owner_last_name",
        ),
        migrations.RemoveField(
            model_name="hirlproject",
            name="owner_phone",
        ),
        migrations.RemoveField(
            model_name="hirlproject",
            name="party_named_on_certificate",
        ),
        migrations.RemoveField(
            model_name="hirlproject",
            name="project_contact_email",
        ),
        migrations.RemoveField(
            model_name="hirlproject",
            name="project_contact_first_name",
        ),
        migrations.RemoveField(
            model_name="hirlproject",
            name="project_contact_last_name",
        ),
        migrations.RemoveField(
            model_name="hirlproject",
            name="project_contact_phone_number",
        ),
        migrations.RemoveField(
            model_name="hirlproject",
            name="project_type",
        ),
        migrations.RemoveField(
            model_name="hirlproject",
            name="registration_user",
        ),
        migrations.RemoveField(
            model_name="hirlproject",
            name="sales_email",
        ),
        migrations.RemoveField(
            model_name="hirlproject",
            name="sales_phone",
        ),
        migrations.RemoveField(
            model_name="hirlproject",
            name="sales_website_url",
        ),
        migrations.RemoveField(
            model_name="hirlproject",
            name="seeking_fannie_mae_green_financing",
        ),
        migrations.RemoveField(
            model_name="hirlproject",
            name="seeking_freddie_mac_green_financing",
        ),
        migrations.RemoveField(
            model_name="hirlproject",
            name="seeking_hud_mortgage_insurance_premium_reduction",
        ),
        migrations.RemoveField(
            model_name="hirlproject",
            name="state",
        ),
        migrations.RemoveField(
            model_name="hirlproject",
            name="state_change_reason",
        ),
        migrations.RemoveField(
            model_name="hirlproject",
            name="state_changed_at",
        ),
        migrations.RemoveField(
            model_name="historicalhirlproject",
            name="application_packet_completion",
        ),
        migrations.RemoveField(
            model_name="historicalhirlproject",
            name="architect_email",
        ),
        migrations.RemoveField(
            model_name="historicalhirlproject",
            name="architect_first_name",
        ),
        migrations.RemoveField(
            model_name="historicalhirlproject",
            name="architect_last_name",
        ),
        migrations.RemoveField(
            model_name="historicalhirlproject",
            name="architect_organization",
        ),
        migrations.RemoveField(
            model_name="historicalhirlproject",
            name="architect_phone",
        ),
        migrations.RemoveField(
            model_name="historicalhirlproject",
            name="billing_email",
        ),
        migrations.RemoveField(
            model_name="historicalhirlproject",
            name="billing_first_name",
        ),
        migrations.RemoveField(
            model_name="historicalhirlproject",
            name="billing_last_name",
        ),
        migrations.RemoveField(
            model_name="historicalhirlproject",
            name="billing_phone",
        ),
        migrations.RemoveField(
            model_name="historicalhirlproject",
            name="builder_email",
        ),
        migrations.RemoveField(
            model_name="historicalhirlproject",
            name="builder_first_name",
        ),
        migrations.RemoveField(
            model_name="historicalhirlproject",
            name="builder_last_name",
        ),
        migrations.RemoveField(
            model_name="historicalhirlproject",
            name="builder_organization",
        ),
        migrations.RemoveField(
            model_name="historicalhirlproject",
            name="builder_phone_number",
        ),
        migrations.RemoveField(
            model_name="historicalhirlproject",
            name="building_will_include_non_residential_space",
        ),
        migrations.RemoveField(
            model_name="historicalhirlproject",
            name="community_named_on_certificate",
        ),
        migrations.RemoveField(
            model_name="historicalhirlproject",
            name="community_owner_organization",
        ),
        migrations.RemoveField(
            model_name="historicalhirlproject",
            name="developer_email",
        ),
        migrations.RemoveField(
            model_name="historicalhirlproject",
            name="developer_first_name",
        ),
        migrations.RemoveField(
            model_name="historicalhirlproject",
            name="developer_last_name",
        ),
        migrations.RemoveField(
            model_name="historicalhirlproject",
            name="developer_organization",
        ),
        migrations.RemoveField(
            model_name="historicalhirlproject",
            name="developer_phone",
        ),
        migrations.RemoveField(
            model_name="historicalhirlproject",
            name="entity_responsible_for_payment",
        ),
        migrations.RemoveField(
            model_name="historicalhirlproject",
            name="intended_to_be_affordable_housing",
        ),
        migrations.RemoveField(
            model_name="historicalhirlproject",
            name="marketing_email",
        ),
        migrations.RemoveField(
            model_name="historicalhirlproject",
            name="marketing_first_name",
        ),
        migrations.RemoveField(
            model_name="historicalhirlproject",
            name="marketing_last_name",
        ),
        migrations.RemoveField(
            model_name="historicalhirlproject",
            name="marketing_phone",
        ),
        migrations.RemoveField(
            model_name="historicalhirlproject",
            name="multi_family_number_of_units",
        ),
        migrations.RemoveField(
            model_name="historicalhirlproject",
            name="multi_family_project_client",
        ),
        migrations.RemoveField(
            model_name="historicalhirlproject",
            name="multi_family_project_description",
        ),
        migrations.RemoveField(
            model_name="historicalhirlproject",
            name="multi_family_project_estimated_completion_date",
        ),
        migrations.RemoveField(
            model_name="historicalhirlproject",
            name="multi_family_project_name",
        ),
        migrations.RemoveField(
            model_name="historicalhirlproject",
            name="multi_family_project_website_url",
        ),
        migrations.RemoveField(
            model_name="historicalhirlproject",
            name="name_to_be_listed_on_commercial_certificate",
        ),
        migrations.RemoveField(
            model_name="historicalhirlproject",
            name="owner_email",
        ),
        migrations.RemoveField(
            model_name="historicalhirlproject",
            name="owner_first_name",
        ),
        migrations.RemoveField(
            model_name="historicalhirlproject",
            name="owner_last_name",
        ),
        migrations.RemoveField(
            model_name="historicalhirlproject",
            name="owner_phone",
        ),
        migrations.RemoveField(
            model_name="historicalhirlproject",
            name="party_named_on_certificate",
        ),
        migrations.RemoveField(
            model_name="historicalhirlproject",
            name="project_contact_email",
        ),
        migrations.RemoveField(
            model_name="historicalhirlproject",
            name="project_contact_first_name",
        ),
        migrations.RemoveField(
            model_name="historicalhirlproject",
            name="project_contact_last_name",
        ),
        migrations.RemoveField(
            model_name="historicalhirlproject",
            name="project_contact_phone_number",
        ),
        migrations.RemoveField(
            model_name="historicalhirlproject",
            name="project_type",
        ),
        migrations.RemoveField(
            model_name="historicalhirlproject",
            name="registration_user",
        ),
        migrations.RemoveField(
            model_name="historicalhirlproject",
            name="sales_email",
        ),
        migrations.RemoveField(
            model_name="historicalhirlproject",
            name="sales_phone",
        ),
        migrations.RemoveField(
            model_name="historicalhirlproject",
            name="sales_website_url",
        ),
        migrations.RemoveField(
            model_name="historicalhirlproject",
            name="seeking_fannie_mae_green_financing",
        ),
        migrations.RemoveField(
            model_name="historicalhirlproject",
            name="seeking_freddie_mac_green_financing",
        ),
        migrations.RemoveField(
            model_name="historicalhirlproject",
            name="seeking_hud_mortgage_insurance_premium_reduction",
        ),
        migrations.RemoveField(
            model_name="historicalhirlproject",
            name="state",
        ),
        migrations.RemoveField(
            model_name="historicalhirlproject",
            name="state_change_reason",
        ),
        migrations.RemoveField(
            model_name="historicalhirlproject",
            name="state_changed_at",
        ),
        migrations.CreateModel(
            name="HIRLProjectRegistration",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
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
                ("state_changed_at", models.DateTimeField(auto_now_add=True)),
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
                ("multi_family_number_of_units", models.IntegerField(blank=True, null=True)),
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
                (
                    "architect_organization",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="company.architectorganization",
                    ),
                ),
                (
                    "builder_organization",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="company.builderorganization",
                    ),
                ),
                (
                    "community_owner_organization",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="company.communityownerorganization",
                    ),
                ),
                (
                    "developer_organization",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="company.developerorganization",
                    ),
                ),
                (
                    "registration_user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="customer_hirl_projects",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]