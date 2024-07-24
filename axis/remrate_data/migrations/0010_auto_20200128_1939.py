# Generated by Django 1.11.26 on 2020-01-28 19:39

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("remrate_data", "0009_auto_20190725_1619"),
    ]

    operations = [
        migrations.AlterField(
            model_name="duct",
            name="location",
            field=models.IntegerField(
                choices=[
                    (1, "Open crawl/raised floor"),
                    (2, "Enclosed crawl space"),
                    (3, "Conditioned crawl space"),
                    (4, "Unconditioned basement"),
                    (5, "Conditioned basement"),
                    (16, "Sealed Attic"),
                    (6, "Attic, under insulation"),
                    (7, "Attic, exposed"),
                    (8, "Conditioned space"),
                    (10, "Garage"),
                    (14, "Floor cavity over garage"),
                    (13, "Exterior wall"),
                    (9, "Wall with no top plate Garage"),
                    (15, "Under slab floor"),
                    (12, "Mobile home belly"),
                    (0, "None"),
                ],
                db_column="nDULoc",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="ductsystem",
            name="conditioned_floor_area",
            field=models.FloatField(db_column="fDSCFArea", help_text="Sq. Feet Served", null=True),
        ),
        migrations.AlterField(
            model_name="ductsystem",
            name="cooling_equipment_number",
            field=models.IntegerField(db_column="lDSClgNo", help_text="Clg Equip", null=True),
        ),
        migrations.AlterField(
            model_name="ductsystem",
            name="duct_leakage_input_type",
            field=models.IntegerField(
                blank=True,
                choices=[(0, "Measured"), (1, "Threshold"), (2, "Qualitative Default")],
                db_column="nDSInpType",
                help_text="Leakage Input",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="ductsystem",
            name="duct_leakage_leakage_to_outside_type",
            field=models.IntegerField(
                blank=True,
                choices=[(2, "Total Leakage"), (3, "Supply and Return Leakage")],
                db_column="nDSLtOType",
                help_text="Radio Button Leakage to Outside",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="ductsystem",
            name="energy_star_test_exemption",
            field=models.BooleanField(
                null=True, db_column="nDSESTAREx", help_text="ENERGY STAR LtO"
            ),
        ),
        migrations.AlterField(
            model_name="ductsystem",
            name="field_test_leakage_to_outside",
            field=models.FloatField(
                blank=True, db_column="fDSTestLtO", help_text="Final LtO Total", null=True
            ),
        ),
        migrations.AlterField(
            model_name="ductsystem",
            name="field_test_total_duct_leakage",
            field=models.FloatField(
                blank=True, db_column="fDSTestDL", help_text="Final Total DL", null=True
            ),
        ),
        migrations.AlterField(
            model_name="ductsystem",
            name="heating_equipment_number",
            field=models.IntegerField(db_column="lDSHtgNo", help_text="Htg Equip", null=True),
        ),
        migrations.AlterField(
            model_name="ductsystem",
            name="iecc_test_exemption",
            field=models.BooleanField(null=True, db_column="nDSIECCEx", help_text="IECC"),
        ),
        migrations.AlterField(
            model_name="ductsystem",
            name="leakage_test_type",
            field=models.IntegerField(
                blank=True,
                choices=[(1, "Both Tested"), (2, "Leakage to Outside"), (3, "Total Duct Leakage")],
                db_column="nDSTestType",
                help_text="Test Type",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="ductsystem",
            name="leakage_tightness_test",
            field=models.IntegerField(
                choices=[
                    (1, "Postconstruction Test"),
                    (2, "Rough-In Test - w/ Air Handler"),
                    (3, "Rough-In Test - w/o Air Handler"),
                    (4, "Duct Leakage Exemption"),
                ],
                db_column="nDSDLeakTT",
                help_text="Duct Test Conditions",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="ductsystem",
            name="leakage_unit",
            field=models.IntegerField(
                choices=[
                    (1, "CFM @ 50 Pascals"),
                    (2, "CFM @ 25 Pascals"),
                    (3, "ACH @ 50 Pascals"),
                    (4, "Natural ACH"),
                    (5, "Eff. Leakage Area (in²)"),
                    (6, "ELA/100 sf shell"),
                    (7, "Thermal Efficiency (%)"),
                    (9, "Specific Leakage Area"),
                    (10, "CFM per Std 152"),
                    (11, "CFM25 / CFA"),
                    (12, "CFM25 / CFMfan"),
                ],
                db_column="nDSDLeakUn",
                help_text="Units of Measure",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="ductsystem",
            name="name",
            field=models.CharField(
                blank=True, db_column="szDSName", help_text="Name", max_length=93
            ),
        ),
        migrations.AlterField(
            model_name="ductsystem",
            name="number_of_return_registers",
            field=models.IntegerField(db_column="lDSRegis", help_text="# Return Grills", null=True),
        ),
        migrations.AlterField(
            model_name="ductsystem",
            name="resnet_test_exemption",
            field=models.BooleanField(null=True, db_column="nDSRESNETEx", help_text="RESNET 2019"),
        ),
        migrations.AlterField(
            model_name="ductsystem",
            name="return_area",
            field=models.FloatField(db_column="fDSRetArea", help_text="Return", null=True),
        ),
        migrations.AlterField(
            model_name="ductsystem",
            name="supply_area",
            field=models.FloatField(db_column="fDSSupArea", help_text="Supply", null=True),
        ),
        migrations.AlterField(
            model_name="ductsystem",
            name="total_real_leakage",
            field=models.FloatField(
                db_column="fDSDLeakRTo", help_text="Total Duct Leakage", null=True
            ),
        ),
        migrations.AlterField(
            model_name="generalmechanicalequipment",
            name="duct_location_1",
            field=models.IntegerField(
                blank=True,
                choices=[
                    (1, "Open crawl/raised floor"),
                    (2, "Enclosed crawl space"),
                    (3, "Conditioned crawl space"),
                    (4, "Unconditioned basement"),
                    (5, "Conditioned basement"),
                    (16, "Sealed Attic"),
                    (6, "Attic, under insulation"),
                    (7, "Attic, exposed"),
                    (8, "Conditioned space"),
                    (10, "Garage"),
                    (14, "Floor cavity over garage"),
                    (13, "Exterior wall"),
                    (9, "Wall with no top plate Garage"),
                    (15, "Under slab floor"),
                    (12, "Mobile home belly"),
                    (0, "None"),
                ],
                db_column="nEIDuctLoc",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="generalmechanicalequipment",
            name="duct_location_2",
            field=models.IntegerField(
                blank=True,
                choices=[
                    (1, "Open crawl/raised floor"),
                    (2, "Enclosed crawl space"),
                    (3, "Conditioned crawl space"),
                    (4, "Unconditioned basement"),
                    (5, "Conditioned basement"),
                    (16, "Sealed Attic"),
                    (6, "Attic, under insulation"),
                    (7, "Attic, exposed"),
                    (8, "Conditioned space"),
                    (10, "Garage"),
                    (14, "Floor cavity over garage"),
                    (13, "Exterior wall"),
                    (9, "Wall with no top plate Garage"),
                    (15, "Under slab floor"),
                    (12, "Mobile home belly"),
                    (0, "None"),
                ],
                db_column="nEIDuctLo2",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="generalmechanicalequipment",
            name="duct_location_3",
            field=models.IntegerField(
                blank=True,
                choices=[
                    (1, "Open crawl/raised floor"),
                    (2, "Enclosed crawl space"),
                    (3, "Conditioned crawl space"),
                    (4, "Unconditioned basement"),
                    (5, "Conditioned basement"),
                    (16, "Sealed Attic"),
                    (6, "Attic, under insulation"),
                    (7, "Attic, exposed"),
                    (8, "Conditioned space"),
                    (10, "Garage"),
                    (14, "Floor cavity over garage"),
                    (13, "Exterior wall"),
                    (9, "Wall with no top plate Garage"),
                    (15, "Under slab floor"),
                    (12, "Mobile home belly"),
                    (0, "None"),
                ],
                db_column="nEIDuctLo3",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="window",
            name="wall_number",
            field=models.IntegerField(db_column="nWDSurfNum", null=True),
        ),
    ]
