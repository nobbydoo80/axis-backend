# Generated by Django 1.11.17 on 2019-06-27 23:26

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("remrate_data", "0007_auto_20190530_1854"),
    ]

    operations = [
        migrations.AddField(
            model_name="buildinginfo",
            name="foundation_within_infiltration_volume",
            field=models.BooleanField(
                null=True, db_column="NBIINFLTVOL", help_text="Is Foundation in Infilt Volume"
            ),
        ),
        migrations.AddField(
            model_name="ductsystem",
            name="leakage_test_type",
            field=models.IntegerField(
                blank=True,
                choices=[(1, "Both"), (2, "Leakage to Outside"), (3, "Total Duct Leakage")],
                db_column="nDSTestType",
                help_text="DuctTestType",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="ductsystem",
            name="no_building_cavities_used_as_ducts",
            field=models.BooleanField(
                null=True, db_column="nDSIsDucted", help_text="No Building cavities used as ducts"
            ),
        ),
        migrations.AddField(
            model_name="energystar",
            name="energy_star_v1p0_mf_hers_index",
            field=models.FloatField(
                blank=True,
                db_column="FV10MFHERS",
                null=True,
                verbose_name="ENERGYSTAR v1.0 Multi-Family NC - HERS Index Target",
            ),
        ),
        migrations.AddField(
            model_name="energystar",
            name="energy_star_v1p0_mf_pv_score",
            field=models.FloatField(
                blank=True,
                db_column="FV10MFHERSPV",
                null=True,
                verbose_name="ENERGYSTAR v1.0 Multi-Family NC - HERS PV Adjusted",
            ),
        ),
        migrations.AddField(
            model_name="energystar",
            name="energy_star_v1p1_mf_hers_index",
            field=models.FloatField(
                blank=True,
                db_column="FV11MFHERS",
                null=True,
                verbose_name="ENERGYSTAR v1.1 Multi-Family NC- HERS Index Target",
            ),
        ),
        migrations.AddField(
            model_name="energystar",
            name="energy_star_v1p1_mf_pv_score",
            field=models.FloatField(
                blank=True,
                db_column="FV11MFHERSPV",
                null=True,
                verbose_name="ENERGYSTAR v1.1 Multi-Family NC - HERS PV Adjusted",
            ),
        ),
        migrations.AddField(
            model_name="energystar",
            name="energy_star_v1p2_mf_hers_index",
            field=models.FloatField(
                blank=True,
                db_column="FV12MFHERS",
                null=True,
                verbose_name="ENERGYSTAR v1.2 Multi-Family NC- HERS Index Target",
            ),
        ),
        migrations.AddField(
            model_name="energystar",
            name="energy_star_v1p2_mf_pv_score",
            field=models.FloatField(
                blank=True,
                db_column="FV12MFHERSPV",
                null=True,
                verbose_name="ENERGYSTAR v1.2 Multi-Family NC - HERS PV Adjusted",
            ),
        ),
        migrations.AddField(
            model_name="energystar",
            name="passes_energy_star_v1p0_mf",
            field=models.BooleanField(
                null=True,
                db_column="bESTARV10MF",
                verbose_name="Meets Energy Star v1.0 Multi-Family NC",
            ),
        ),
        migrations.AddField(
            model_name="energystar",
            name="passes_energy_star_v1p1_mf",
            field=models.BooleanField(
                null=True,
                db_column="BESTARV11MF",
                verbose_name="Meets Energy Star v1.1 Multi-Family NC",
            ),
        ),
        migrations.AddField(
            model_name="energystar",
            name="passes_energy_star_v1p2_mf",
            field=models.BooleanField(
                null=True,
                db_column="BESTARV12MF",
                verbose_name="Meets Energy Star v1.2 Multi-Family NC",
            ),
        ),
        migrations.AddField(
            model_name="infiltration",
            name="no_mechanical_vent_measured",
            field=models.BooleanField(
                null=True, db_column="NINNOMVMSRD", verbose_name="No Mech Vent Measured"
            ),
        ),
        migrations.AddField(
            model_name="infiltration",
            name="use_fan_watts_defaults",
            field=models.BooleanField(
                null=True, db_column="NINWATTDFLT", verbose_name="Fan Watts Use Defaults"
            ),
        ),
        migrations.AlterField(
            model_name="energystar",
            name="energy_star_v2p5_hers_saf",
            field=models.FloatField(
                blank=True,
                db_column="FV25SZADJF",
                null=True,
                verbose_name="ENERGYSTAR v2.5 size adjustment factor",
            ),
        ),
        migrations.AlterField(
            model_name="energystar",
            name="energy_star_v2p5_hers_saf_score",
            field=models.FloatField(
                blank=True,
                db_column="FV25HERSSA",
                null=True,
                verbose_name="ENERGYSTAR v2.5 size adjustment factor adjusted HERS score",
            ),
        ),
        migrations.AlterField(
            model_name="energystar",
            name="energy_star_v2p5_hers_score",
            field=models.FloatField(
                blank=True,
                db_column="FV25HERS",
                null=True,
                verbose_name="ENERGYSTAR v2.5 Reference Design HERS score",
            ),
        ),
        migrations.AlterField(
            model_name="energystar",
            name="energy_star_v2p5_pv_score",
            field=models.FloatField(
                blank=True,
                db_column="FV25HERSPV",
                null=True,
                verbose_name="ENERGYSTAR v2.5 photo voltaic adjusted HERS score",
            ),
        ),
        migrations.AlterField(
            model_name="energystar",
            name="energy_star_v3_hers_saf",
            field=models.FloatField(
                blank=True,
                db_column="FV3SZADJF",
                null=True,
                verbose_name="ENERGYSTAR v3.0 size adjustment factor",
            ),
        ),
        migrations.AlterField(
            model_name="energystar",
            name="energy_star_v3_hers_saf_score",
            field=models.FloatField(
                blank=True,
                db_column="FV3HERSSA",
                null=True,
                verbose_name="ENERGYSTAR v3.0 size adjustment factor adjusted HERS score",
            ),
        ),
        migrations.AlterField(
            model_name="energystar",
            name="energy_star_v3_hers_score",
            field=models.FloatField(
                blank=True,
                db_column="FV3HERS",
                null=True,
                verbose_name="ENERGYSTAR v3.0 Reference Design HERS score",
            ),
        ),
        migrations.AlterField(
            model_name="energystar",
            name="energy_star_v3_hi_hers_saf",
            field=models.FloatField(
                blank=True,
                db_column="FV3HISZADJF",
                null=True,
                verbose_name="ENERGYSTAR v3.0 Hawaii, Guam size adjustment factor",
            ),
        ),
        migrations.AlterField(
            model_name="energystar",
            name="energy_star_v3_hi_hers_saf_score",
            field=models.FloatField(
                blank=True,
                db_column="FV3HIHERSSA",
                null=True,
                verbose_name="ENERGYSTAR v3.0 Hawaii, Guam size adjustment factor adjusted HERS score",
            ),
        ),
        migrations.AlterField(
            model_name="energystar",
            name="energy_star_v3_hi_hers_score",
            field=models.FloatField(
                blank=True,
                db_column="FV3HIHERS",
                null=True,
                verbose_name="ENERGYSTAR v3.0 Hawaii, Guam Reference Design HERS score",
            ),
        ),
        migrations.AlterField(
            model_name="energystar",
            name="energy_star_v3_hi_pv_score",
            field=models.FloatField(
                blank=True,
                db_column="FV3HIHERSPV",
                null=True,
                verbose_name="ENERGYSTAR v3.0 Hawaii, Guam photo voltaic adjusted HERS score",
            ),
        ),
        migrations.AlterField(
            model_name="energystar",
            name="energy_star_v3_pv_score",
            field=models.FloatField(
                blank=True,
                db_column="FV3HERSPV",
                null=True,
                verbose_name="ENERGYSTAR v3.0 photo voltaic adjusted HERS score",
            ),
        ),
        migrations.AlterField(
            model_name="energystar",
            name="energy_star_v3p1_hers_saf",
            field=models.FloatField(
                blank=True,
                db_column="FV31SZADJF",
                null=True,
                verbose_name="ENERGYSTAR v3.1 size adjustment factor",
            ),
        ),
        migrations.AlterField(
            model_name="energystar",
            name="energy_star_v3p1_hers_saf_score",
            field=models.FloatField(
                blank=True,
                db_column="FV31HERSSA",
                null=True,
                verbose_name="ENERGYSTAR v3.1 size adjustment factor adjusted HERS score",
            ),
        ),
        migrations.AlterField(
            model_name="energystar",
            name="energy_star_v3p1_hers_score",
            field=models.FloatField(
                blank=True,
                db_column="FV31HERS",
                null=True,
                verbose_name="ENERGYSTAR v3.1 Reference Design HERS score",
            ),
        ),
        migrations.AlterField(
            model_name="energystar",
            name="energy_star_v3p1_pv_score",
            field=models.FloatField(
                blank=True,
                db_column="FV31HERSPV",
                null=True,
                verbose_name="ENERGYSTAR v3.1 photo voltaic adjusted HERS score",
            ),
        ),
        migrations.AlterField(
            model_name="energystar",
            name="energy_star_v3p2_pv_score",
            field=models.FloatField(
                blank=True,
                db_column="FV32WHERSPV",
                null=True,
                verbose_name="ENERGYSTAR v3.2 Washington photo voltaic adjusted HERS score",
            ),
        ),
        migrations.AlterField(
            model_name="energystar",
            name="energy_star_v3p2_whers_saf",
            field=models.FloatField(
                blank=True,
                db_column="FV32WSZADJF",
                null=True,
                verbose_name="ENERGYSTAR v3.2 Washington size adjustment factor",
            ),
        ),
        migrations.AlterField(
            model_name="energystar",
            name="energy_star_v3p2_whers_saf_score",
            field=models.FloatField(
                blank=True,
                db_column="FV32WHERSSA",
                null=True,
                verbose_name="ENERGYSTAR v3.2 Washington size adjustment factor adjusted HERS score",
            ),
        ),
        migrations.AlterField(
            model_name="energystar",
            name="energy_star_v3p2_whers_score",
            field=models.FloatField(
                blank=True,
                db_column="FV32WHERS",
                null=True,
                verbose_name="ENERGYSTAR v3.2 Washington Reference Design HERS score",
            ),
        ),
        migrations.AlterField(
            model_name="energystar",
            name="passes_energy_star_v2",
            field=models.BooleanField(
                null=True,
                db_column="BESTARV2",
                default=False,
                verbose_name="Passes ENERGYSTAR v2.0",
            ),
        ),
        migrations.AlterField(
            model_name="energystar",
            name="passes_energy_star_v2p5",
            field=models.BooleanField(
                null=True,
                db_column="BESTARV25",
                default=False,
                verbose_name="Passes ENERGYSTAR v2.5",
            ),
        ),
        migrations.AlterField(
            model_name="energystar",
            name="passes_energy_star_v3",
            field=models.BooleanField(
                null=True,
                db_column="BESTARV3",
                default=False,
                verbose_name="Passes ENERGYSTAR v3.0",
            ),
        ),
        migrations.AlterField(
            model_name="energystar",
            name="passes_energy_star_v3_hi",
            field=models.BooleanField(
                null=True,
                db_column="BESTARV3HI",
                default=False,
                verbose_name="Passes ENERGYSTAR v3.0 Hawaii, Guam",
            ),
        ),
        migrations.AlterField(
            model_name="energystar",
            name="passes_energy_star_v3p1",
            field=models.BooleanField(
                null=True,
                db_column="BESTARV31",
                default=False,
                verbose_name="Passes ENERGYSTAR v3.1",
            ),
        ),
        migrations.AlterField(
            model_name="energystar",
            name="passes_energy_star_v3p2",
            field=models.BooleanField(
                null=True,
                db_column="BESTARV32W",
                default=False,
                verbose_name="Passes ENERGYSTAR v3.2 Washington",
            ),
        ),
    ]
