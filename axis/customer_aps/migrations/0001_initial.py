# Generated by Django 1.11.16 on 2018-10-08 18:15

import axis.geographic.placedmodels
from django.db import migrations, models
import django.db.models.deletion
import localflavor.us.models
import simple_history.models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("company", "0001_initial"),
        ("eep_program", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="APSHome",
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
                    "street_line1",
                    models.CharField(
                        blank=True,
                        help_text="Enter the street number and street name of the home (e.g. 123 Main St).",
                        max_length=100,
                        null=True,
                        verbose_name="Street Address",
                    ),
                ),
                (
                    "street_line2",
                    models.CharField(
                        blank=True,
                        help_text="Enter the unit number (where multiple dwelling units share a common street address), or leave blank if not applicable.",
                        max_length=100,
                        null=True,
                        verbose_name="Unit number (if applicable)",
                    ),
                ),
                (
                    "zipcode",
                    models.CharField(
                        help_text="Enter the 5-digit ZIP Code of home.",
                        max_length=15,
                        null=True,
                        verbose_name="ZIP Code",
                    ),
                ),
                (
                    "lot_number",
                    models.CharField(
                        blank=True,
                        help_text='Enter the lot number of the home (typical for a "production builder" in a subdivision or development of multiple homes), or leave blank or "N/A" if unknown or not applicable.',
                        max_length=16,
                        null=True,
                        verbose_name="Lot number",
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
                ("aps_id", models.CharField(blank=True, max_length=32, null=True, unique=True)),
                ("premise_id", models.CharField(blank=True, max_length=32, null=True, unique=True)),
                ("raw_lot_number", models.CharField(blank=True, max_length=32, null=True)),
                ("raw_street_number", models.CharField(blank=True, max_length=64, null=True)),
                ("raw_prefix", models.CharField(blank=True, max_length=64, null=True)),
                ("raw_street_name", models.CharField(blank=True, max_length=255, null=True)),
                ("raw_suffix", models.CharField(blank=True, max_length=64, null=True)),
                ("raw_street_line_1", models.CharField(blank=True, max_length=100, null=True)),
                ("raw_street_line_2", models.CharField(blank=True, max_length=64, null=True)),
                ("raw_city", models.CharField(blank=True, max_length=64, null=True)),
                ("raw_state", models.CharField(blank=True, max_length=16, null=True)),
                ("raw_zip", models.CharField(blank=True, max_length=12, null=True)),
                ("meterset_date", models.DateField(blank=True, null=True)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={"verbose_name": "APS Exported Home"},
            bases=(axis.geographic.placedmodels.PlaceSynchronizationMixin, models.Model),
        ),
        migrations.CreateModel(
            name="HistoricalAPSHome",
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
                    "street_line1",
                    models.CharField(
                        blank=True,
                        help_text="Enter the street number and street name of the home (e.g. 123 Main St).",
                        max_length=100,
                        null=True,
                        verbose_name="Street Address",
                    ),
                ),
                (
                    "street_line2",
                    models.CharField(
                        blank=True,
                        help_text="Enter the unit number (where multiple dwelling units share a common street address), or leave blank if not applicable.",
                        max_length=100,
                        null=True,
                        verbose_name="Unit number (if applicable)",
                    ),
                ),
                (
                    "zipcode",
                    models.CharField(
                        help_text="Enter the 5-digit ZIP Code of home.",
                        max_length=15,
                        null=True,
                        verbose_name="ZIP Code",
                    ),
                ),
                (
                    "lot_number",
                    models.CharField(
                        blank=True,
                        help_text='Enter the lot number of the home (typical for a "production builder" in a subdivision or development of multiple homes), or leave blank or "N/A" if unknown or not applicable.',
                        max_length=16,
                        null=True,
                        verbose_name="Lot number",
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
                ("aps_id", models.CharField(blank=True, db_index=True, max_length=32, null=True)),
                (
                    "premise_id",
                    models.CharField(blank=True, db_index=True, max_length=32, null=True),
                ),
                ("raw_lot_number", models.CharField(blank=True, max_length=32, null=True)),
                ("raw_street_number", models.CharField(blank=True, max_length=64, null=True)),
                ("raw_prefix", models.CharField(blank=True, max_length=64, null=True)),
                ("raw_street_name", models.CharField(blank=True, max_length=255, null=True)),
                ("raw_suffix", models.CharField(blank=True, max_length=64, null=True)),
                ("raw_street_line_1", models.CharField(blank=True, max_length=100, null=True)),
                ("raw_street_line_2", models.CharField(blank=True, max_length=64, null=True)),
                ("raw_city", models.CharField(blank=True, max_length=64, null=True)),
                ("raw_state", models.CharField(blank=True, max_length=16, null=True)),
                ("raw_zip", models.CharField(blank=True, max_length=12, null=True)),
                ("meterset_date", models.DateField(blank=True, null=True)),
                ("is_active", models.BooleanField(default=True)),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                ("history_date", models.DateTimeField()),
                (
                    "history_type",
                    models.CharField(
                        choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")], max_length=1
                    ),
                ),
            ],
            options={
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": "history_date",
                "verbose_name": "historical APS Exported Home",
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="LegacyAPSBuilder",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("aps_id", models.CharField(max_length=32)),
                ("active", models.BooleanField(default=False)),
                ("bldr_comment", models.CharField(blank=True, max_length=255, null=True)),
                ("bldr_id", models.CharField(blank=True, max_length=5, null=True)),
                ("charge_no", models.CharField(blank=True, max_length=7, null=True)),
                ("dba", models.CharField(blank=True, max_length=32, null=True)),
                ("fax", models.CharField(blank=True, max_length=12, null=True)),
                ("mail_addr1", models.CharField(blank=True, max_length=32, null=True)),
                ("mail_addr2", models.CharField(blank=True, max_length=16, null=True)),
                ("mail_city", models.CharField(blank=True, max_length=32, null=True)),
                ("mail_state", models.CharField(blank=True, max_length=4, null=True)),
                ("mail_zip", models.CharField(blank=True, max_length=16, null=True)),
                ("pay_point", models.CharField(blank=True, max_length=5, null=True)),
                ("phone", models.CharField(blank=True, max_length=16, null=True)),
                ("phone2", models.CharField(blank=True, max_length=5, null=True)),
                ("site_addr", models.CharField(blank=True, max_length=32, null=True)),
                ("site_city", models.CharField(blank=True, max_length=32, null=True)),
                ("site_state", models.CharField(blank=True, max_length=5, null=True)),
                ("site_zip", models.CharField(blank=True, max_length=9, null=True)),
                ("soalr_charge_no", models.CharField(blank=True, max_length=12, null=True)),
                ("vendor_no", models.CharField(blank=True, max_length=8, null=True)),
                ("web_address", models.CharField(blank=True, max_length=64, null=True)),
                (
                    "builder",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="company.BuilderOrganization",
                    ),
                ),
            ],
            options={"verbose_name": "Legacy APS Builder"},
        ),
        migrations.CreateModel(
            name="LegacyAPSHome",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("addr_dir", models.CharField(blank=True, max_length=4, null=True)),
                ("addr_name", models.CharField(blank=True, max_length=32, null=True)),
                ("addr_no", models.CharField(blank=True, max_length=16, null=True)),
                ("addr_sufx", models.CharField(blank=True, max_length=8, null=True)),
                (
                    "amt_pd",
                    models.DecimalField(
                        blank=True, decimal_places=2, default=0, max_digits=8, null=True
                    ),
                ),
                ("amt_pd_sr", models.CharField(blank=True, max_length=16, null=True)),
                ("append_date", models.DateField(blank=True, null=True)),
                ("ck_numb", models.CharField(blank=True, max_length=16, null=True)),
                ("ck_req_date", models.DateField(blank=True, null=True)),
                ("comments", models.CharField(blank=True, max_length=128, null=True)),
                ("compliance_date", models.DateField(blank=True, null=True)),
                ("dev", models.CharField(blank=True, max_length=64, null=True)),
                (
                    "h2_opv_pd",
                    models.DecimalField(
                        blank=True, decimal_places=2, default=0, max_digits=8, null=True
                    ),
                ),
                ("initial_meter_set", models.CharField(blank=True, max_length=32, null=True)),
                ("lot_no", models.CharField(blank=True, max_length=16, null=True)),
                ("lot_recno", models.CharField(blank=True, max_length=16, null=True)),
                ("lot_status", models.CharField(blank=True, max_length=16, null=True)),
                ("lt_city", models.CharField(blank=True, max_length=32, null=True)),
                ("lt_state", models.CharField(blank=True, max_length=12, null=True)),
                ("lt_zip", models.CharField(blank=True, max_length=16, null=True)),
                ("pd_date", models.DateField(blank=True, null=True)),
                ("pd_date_sr", models.DateField(blank=True, null=True)),
                ("plan_no", models.CharField(blank=True, max_length=12, null=True)),
                ("aps_id", models.CharField(blank=True, max_length=32, null=True)),
                ("solar_ready", models.CharField(blank=True, max_length=4, null=True)),
                ("solar_type", models.CharField(blank=True, max_length=8, null=True)),
                ("legacy_import_comment", models.CharField(blank=True, max_length=256, null=True)),
                ("is_legacy", models.BooleanField(default=True)),
                (
                    "aps_home",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="customer_aps.APSHome",
                    ),
                ),
                (
                    "eep_program",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="eep_program.EEPProgram",
                    ),
                ),
                (
                    "legacy_builder",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="customer_aps.LegacyAPSBuilder",
                    ),
                ),
            ],
            options={"verbose_name": "Legacy APS Home"},
        ),
        migrations.CreateModel(
            name="LegacyAPSSubdivision",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("aps_id", models.CharField(blank=True, max_length=32, null=True)),
                ("active", models.BooleanField(default=False)),
                ("addendum_date", models.DateField(blank=True, null=True)),
                ("addendum_lots", models.CharField(blank=True, max_length=8, null=True)),
                ("ammended_date", models.DateField(blank=True, null=True)),
                ("ammended_lots", models.CharField(blank=True, max_length=8, null=True)),
                ("contract_date", models.DateField(blank=True, null=True)),
                ("exp_date", models.DateField(blank=True, null=True)),
                ("lots_paid", models.CharField(blank=True, max_length=8, null=True)),
                ("lots_signed", models.CharField(blank=True, max_length=8, null=True)),
                ("mstr_plan", models.CharField(blank=True, max_length=64, null=True)),
                ("parcel", models.CharField(blank=True, max_length=24, null=True)),
                ("solar_community", models.CharField(blank=True, max_length=3, null=True)),
                ("sub", models.CharField(blank=True, max_length=64, null=True)),
                ("sub_comment", models.CharField(blank=True, max_length=96, null=True)),
                ("sub_loc_city", models.CharField(blank=True, max_length=32, null=True)),
                ("sub_loc_zip", models.CharField(blank=True, max_length=9, null=True)),
                ("sub_location", models.CharField(blank=True, max_length=64, null=True)),
                ("legacy_import_comment", models.CharField(blank=True, max_length=256, null=True)),
                ("is_legacy", models.BooleanField(default=True)),
                (
                    "legacy_builder",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="customer_aps.LegacyAPSBuilder",
                    ),
                ),
                (
                    "legacy_rater",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="company.Company",
                    ),
                ),
            ],
            options={
                "verbose_name": "Legacy APS Subdivision",
            },
        ),
        migrations.AddField(
            model_name="legacyapshome",
            name="legacy_subdivision",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="customer_aps.LegacyAPSSubdivision",
            ),
        ),
    ]
