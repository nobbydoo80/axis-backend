# Generated by Django 1.11.16 on 2018-10-08 18:15

import datetime

import django.db.models.deletion
import localflavor.us.models
import simple_history.models
from django.conf import settings
from django.db import migrations, models

import axis.geographic.placedmodels
import axis.relationship.models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("company", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("community", "0001_initial"),
        ("floorplan", "0002_auto_20181008_1815"),
        ("geocoder", "0001_initial"),
        ("eep_program", "0001_initial"),
        ("geographic", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="EEPProgramSubdivisionStatus",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("date_added", models.DateField(default=datetime.date.today, editable=False)),
                (
                    "company",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="company.Company"
                    ),
                ),
                (
                    "eep_program",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="eep_program.EEPProgram"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="FloorplanApproval",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("date_added", models.DateField(auto_now_add=True)),
                ("date_modified", models.DateField(auto_now=True, null=True)),
                ("is_approved", models.BooleanField(default=False)),
                (
                    "approved_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "floorplan",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="floorplan.Floorplan"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="HistoricalSubdivision",
            fields=[
                (
                    "id",
                    models.IntegerField(
                        auto_created=True, blank=True, db_index=True, verbose_name="ID"
                    ),
                ),
                ("latitude", models.FloatField(blank=True, null=True)),
                ("longitude", models.FloatField(blank=True, null=True)),
                (
                    "state",
                    localflavor.us.models.USStateField(
                        choices=[
                            (b"AL", "Alabama"),
                            (b"AK", "Alaska"),
                            (b"AS", "American Samoa"),
                            (b"AZ", "Arizona"),
                            (b"AR", "Arkansas"),
                            (b"AA", "Armed Forces Americas"),
                            (b"AE", "Armed Forces Europe"),
                            (b"AP", "Armed Forces Pacific"),
                            (b"CA", "California"),
                            (b"CO", "Colorado"),
                            (b"CT", "Connecticut"),
                            (b"DE", "Delaware"),
                            (b"DC", "District of Columbia"),
                            (b"FL", "Florida"),
                            (b"GA", "Georgia"),
                            (b"GU", "Guam"),
                            (b"HI", "Hawaii"),
                            (b"ID", "Idaho"),
                            (b"IL", "Illinois"),
                            (b"IN", "Indiana"),
                            (b"IA", "Iowa"),
                            (b"KS", "Kansas"),
                            (b"KY", "Kentucky"),
                            (b"LA", "Louisiana"),
                            (b"ME", "Maine"),
                            (b"MD", "Maryland"),
                            (b"MA", "Massachusetts"),
                            (b"MI", "Michigan"),
                            (b"MN", "Minnesota"),
                            (b"MS", "Mississippi"),
                            (b"MO", "Missouri"),
                            (b"MT", "Montana"),
                            (b"NE", "Nebraska"),
                            (b"NV", "Nevada"),
                            (b"NH", "New Hampshire"),
                            (b"NJ", "New Jersey"),
                            (b"NM", "New Mexico"),
                            (b"NY", "New York"),
                            (b"NC", "North Carolina"),
                            (b"ND", "North Dakota"),
                            (b"MP", "Northern Mariana Islands"),
                            (b"OH", "Ohio"),
                            (b"OK", "Oklahoma"),
                            (b"OR", "Oregon"),
                            (b"PA", "Pennsylvania"),
                            (b"PR", "Puerto Rico"),
                            (b"RI", "Rhode Island"),
                            (b"SC", "South Carolina"),
                            (b"SD", "South Dakota"),
                            (b"TN", "Tennessee"),
                            (b"TX", "Texas"),
                            (b"UT", "Utah"),
                            (b"VT", "Vermont"),
                            (b"VI", "Virgin Islands"),
                            (b"VA", "Virginia"),
                            (b"WA", "Washington"),
                            (b"WV", "West Virginia"),
                            (b"WI", "Wisconsin"),
                            (b"WY", "Wyoming"),
                        ],
                        editable=False,
                        max_length=2,
                        null=True,
                        verbose_name="State",
                    ),
                ),
                ("confirmed_address", models.BooleanField(default=False)),
                (
                    "address_override",
                    models.BooleanField(
                        default=False,
                        help_text="Bypass the attempt to normalize the address via a mapping service. Changing address fields after marking this option will unmark it.",
                        verbose_name="Override address",
                    ),
                ),
                (
                    "cross_roads",
                    models.CharField(
                        blank=True,
                        help_text="Enter the crossroads or street intersection of this subdivision or leave blank if unknown.",
                        max_length=128,
                        verbose_name="Crossroads",
                    ),
                ),
                (
                    "is_multi_family",
                    models.BooleanField(
                        default=False,
                        help_text="This denotes a multi-family project, such as an apartment or condo",
                        verbose_name="Multi-family",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text='A subdivision is a parcel of land in which one builder intends to build several homes.  To add a subdivision association or create a new subdivision, type the first few letters of the name of the subdivision that you wish to associate with.  If the subdivision you wish to associate with already exists within the database, select it from the "Select from existing" list and click on "Submit" at the bottom of this page to create the association.  If the subdivision does not exist within the database, type the name of the subdivision, select it in the "Create new" list, and populate the fields below.',
                        max_length=64,
                        verbose_name="Subdivision Name",
                    ),
                ),
                (
                    "builder_name",
                    models.CharField(
                        blank=True,
                        help_text="If applicable, enter an alternate name or identifier for the subdivision such as the accounting code.",
                        max_length=255,
                        null=True,
                        verbose_name="Alternate Name or Code",
                    ),
                ),
                ("use_sampling", models.BooleanField(default=True)),
                ("use_metro_sampling", models.BooleanField(default=True)),
                ("is_active", models.BooleanField(default=True)),
                ("created_date", models.DateTimeField(editable=False)),
                ("modified_date", models.DateTimeField()),
                ("slug", models.SlugField(editable=False, max_length=64)),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                ("history_date", models.DateTimeField()),
                (
                    "history_type",
                    models.CharField(
                        choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")], max_length=1
                    ),
                ),
                (
                    "builder_org",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="company.BuilderOrganization",
                    ),
                ),
                (
                    "city",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="geographic.City",
                    ),
                ),
                (
                    "climate_zone",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="geographic.ClimateZone",
                    ),
                ),
                (
                    "community",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="community.Community",
                    ),
                ),
                (
                    "county",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="geographic.County",
                    ),
                ),
                (
                    "geocode_response",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="geocoder.GeocodeResponse",
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
                    "metro",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="geographic.Metro",
                    ),
                ),
                (
                    "place",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="geographic.Place",
                    ),
                ),
            ],
            options={
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": "history_date",
                "verbose_name": "historical Subdivision",
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="Subdivision",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("latitude", models.FloatField(blank=True, null=True)),
                ("longitude", models.FloatField(blank=True, null=True)),
                (
                    "state",
                    localflavor.us.models.USStateField(
                        choices=[
                            (b"AL", "Alabama"),
                            (b"AK", "Alaska"),
                            (b"AS", "American Samoa"),
                            (b"AZ", "Arizona"),
                            (b"AR", "Arkansas"),
                            (b"AA", "Armed Forces Americas"),
                            (b"AE", "Armed Forces Europe"),
                            (b"AP", "Armed Forces Pacific"),
                            (b"CA", "California"),
                            (b"CO", "Colorado"),
                            (b"CT", "Connecticut"),
                            (b"DE", "Delaware"),
                            (b"DC", "District of Columbia"),
                            (b"FL", "Florida"),
                            (b"GA", "Georgia"),
                            (b"GU", "Guam"),
                            (b"HI", "Hawaii"),
                            (b"ID", "Idaho"),
                            (b"IL", "Illinois"),
                            (b"IN", "Indiana"),
                            (b"IA", "Iowa"),
                            (b"KS", "Kansas"),
                            (b"KY", "Kentucky"),
                            (b"LA", "Louisiana"),
                            (b"ME", "Maine"),
                            (b"MD", "Maryland"),
                            (b"MA", "Massachusetts"),
                            (b"MI", "Michigan"),
                            (b"MN", "Minnesota"),
                            (b"MS", "Mississippi"),
                            (b"MO", "Missouri"),
                            (b"MT", "Montana"),
                            (b"NE", "Nebraska"),
                            (b"NV", "Nevada"),
                            (b"NH", "New Hampshire"),
                            (b"NJ", "New Jersey"),
                            (b"NM", "New Mexico"),
                            (b"NY", "New York"),
                            (b"NC", "North Carolina"),
                            (b"ND", "North Dakota"),
                            (b"MP", "Northern Mariana Islands"),
                            (b"OH", "Ohio"),
                            (b"OK", "Oklahoma"),
                            (b"OR", "Oregon"),
                            (b"PA", "Pennsylvania"),
                            (b"PR", "Puerto Rico"),
                            (b"RI", "Rhode Island"),
                            (b"SC", "South Carolina"),
                            (b"SD", "South Dakota"),
                            (b"TN", "Tennessee"),
                            (b"TX", "Texas"),
                            (b"UT", "Utah"),
                            (b"VT", "Vermont"),
                            (b"VI", "Virgin Islands"),
                            (b"VA", "Virginia"),
                            (b"WA", "Washington"),
                            (b"WV", "West Virginia"),
                            (b"WI", "Wisconsin"),
                            (b"WY", "Wyoming"),
                        ],
                        editable=False,
                        max_length=2,
                        null=True,
                        verbose_name="State",
                    ),
                ),
                ("confirmed_address", models.BooleanField(default=False)),
                (
                    "address_override",
                    models.BooleanField(
                        default=False,
                        help_text="Bypass the attempt to normalize the address via a mapping service. Changing address fields after marking this option will unmark it.",
                        verbose_name="Override address",
                    ),
                ),
                (
                    "cross_roads",
                    models.CharField(
                        blank=True,
                        help_text="Enter the crossroads or street intersection of this subdivision or leave blank if unknown.",
                        max_length=128,
                        verbose_name="Crossroads",
                    ),
                ),
                (
                    "is_multi_family",
                    models.BooleanField(
                        default=False,
                        help_text="This denotes a multi-family project, such as an apartment or condo",
                        verbose_name="Multi-family",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text='A subdivision is a parcel of land in which one builder intends to build several homes.  To add a subdivision association or create a new subdivision, type the first few letters of the name of the subdivision that you wish to associate with.  If the subdivision you wish to associate with already exists within the database, select it from the "Select from existing" list and click on "Submit" at the bottom of this page to create the association.  If the subdivision does not exist within the database, type the name of the subdivision, select it in the "Create new" list, and populate the fields below.',
                        max_length=64,
                        verbose_name="Subdivision Name",
                    ),
                ),
                (
                    "builder_name",
                    models.CharField(
                        blank=True,
                        help_text="If applicable, enter an alternate name or identifier for the subdivision such as the accounting code.",
                        max_length=255,
                        null=True,
                        verbose_name="Alternate Name or Code",
                    ),
                ),
                ("use_sampling", models.BooleanField(default=True)),
                ("use_metro_sampling", models.BooleanField(default=True)),
                ("is_active", models.BooleanField(default=True)),
                ("created_date", models.DateTimeField(editable=False)),
                ("modified_date", models.DateTimeField()),
                ("slug", models.SlugField(editable=False, max_length=64, unique=True)),
                (
                    "builder_org",
                    models.ForeignKey(
                        help_text='Type the first few letters of the name of the Builder that is building all homes in this subdivision, and select the correct company from the list presented.  If the correct company is not available, click "Add New" to add a new Builder or Builder association.',
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="builder_org_subdivisions",
                        to="company.BuilderOrganization",
                        verbose_name="Builder",
                    ),
                ),
                (
                    "city",
                    models.ForeignKey(
                        blank=True,
                        help_text='Type the first few letters of the name of the city of the location and select the correct city/state/county combination from the list presented. If the correct city is not available, click "Add New" to add a city to the database.',
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="geographic.City",
                        verbose_name="City/State/County",
                    ),
                ),
                (
                    "climate_zone",
                    models.ForeignKey(
                        blank=True,
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="geographic.ClimateZone",
                    ),
                ),
                (
                    "community",
                    models.ForeignKey(
                        blank=True,
                        help_text='A community, also known as a "master-planned community", is a parcel of land in which one or more builders intend to build one or more subdivisions.  Select the community from the list presented.  If the correct community is not available, click "Add New" to add a new community or community association.',
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="community.Community",
                        verbose_name="Community Name",
                    ),
                ),
                (
                    "county",
                    models.ForeignKey(
                        blank=True,
                        help_text=None,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="geographic.County",
                        verbose_name="County",
                    ),
                ),
                (
                    "eep_programs",
                    models.ManyToManyField(
                        through="subdivision.EEPProgramSubdivisionStatus",
                        to="eep_program.EEPProgram",
                    ),
                ),
                (
                    "floorplans",
                    models.ManyToManyField(
                        through="subdivision.FloorplanApproval", to="floorplan.Floorplan"
                    ),
                ),
                (
                    "geocode_response",
                    models.ForeignKey(
                        blank=True,
                        help_text="The response this place was constructed from.",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="geocoder.GeocodeResponse",
                    ),
                ),
                (
                    "metro",
                    models.ForeignKey(
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="geographic.Metro",
                        verbose_name="Metro",
                    ),
                ),
                (
                    "place",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="subdivision_set",
                        to="geographic.Place",
                    ),
                ),
            ],
            options={"ordering": ("name", "community"), "verbose_name": "Subdivision"},
            bases=(
                axis.relationship.models.RelationshipUtilsMixin,
                axis.geographic.placedmodels.PlaceSynchronizationMixin,
                models.Model,
            ),
        ),
        migrations.AddField(
            model_name="floorplanapproval",
            name="subdivision",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="subdivision.Subdivision"
            ),
        ),
        migrations.AddField(
            model_name="eepprogramsubdivisionstatus",
            name="subdivision",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="subdivision.Subdivision"
            ),
        ),
        migrations.AlterUniqueTogether(
            name="subdivision",
            unique_together=set([("name", "city", "builder_org", "community")]),
        ),
        migrations.AlterUniqueTogether(
            name="floorplanapproval",
            unique_together=set([("subdivision", "floorplan")]),
        ),
    ]