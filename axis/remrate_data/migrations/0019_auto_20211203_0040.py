# Generated by Django 3.2.9 on 2021-12-03 00:40

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("remrate_data", "0018_alter_datatracker_building"),
    ]

    operations = [
        migrations.RenameField(
            model_name="foundationwalltype",
            old_name="masonary_thickness",
            new_name="masonry_thickness",
        ),
        migrations.AlterField(
            model_name="abovegradewall",
            name="color",
            field=models.IntegerField(
                choices=[
                    (0, "None"),
                    (1, "Light"),
                    (2, "Medium"),
                    (3, "Dark"),
                    (4, "Reflective"),
                    (5, "Std140"),
                    (6, "Std140-lowAbs"),
                    (7, "White Comp. Shingles"),
                    (8, "White Tile/Concrete"),
                    (9, "White Metal/TPO"),
                ],
                db_column="nAGCol",
            ),
        ),
        migrations.AlterField(
            model_name="foundationwall",
            name="location",
            field=models.IntegerField(
                choices=[
                    (0, "None"),
                    (201, "Between conditioned space and ambient/ground"),
                    (202, "Between conditioned space and garage/ground"),
                    (203, "Between conditioned space and open crawl space/ground"),
                    (205, "Between conditioned space and unconditioned basement/ground"),
                    (206, "Between conditioned space and enclosed crawl space/ground"),
                    (213, "Between cond and another cond unit (adiabatic)"),
                    (229, "Bsmt (conditioned)---ambient/ground"),
                    (230, "Bsmt (conditioned)---ambient/ground"),
                    (231, "Bsmt (conditioned)---garage/ground"),
                    (232, "Bsmt (conditioned)---crawl (conditioned)/ground"),
                    (233, "Bsmt (conditioned)---unconditioned bsmt/ground"),
                    (234, "Bsmt (conditioned)---enclosed crawl/ground"),
                    (235, "Bsmt (conditioned)---open crawl/ground"),
                    (236, "Bsmt (conditioned)---MF unrated cond space (adiabatic)/ground"),
                    (237, "Bsmt (conditioned)---MF unrated heated/ground"),
                    (238, "Bsmt (conditioned)---MF buffer/ground"),
                    (239, "Bsmt (conditioned)---MF nonfreezing/ground"),
                    (214, "Crawl (conditioned)---ambient/ground"),
                    (215, "Crawl (conditioned)---garage/ground"),
                    (216, "Crawl (conditioned)---open crawl/ground"),
                    (239, "Crawl (conditioned)---unconditioned bsmt/ground"),
                    (240, "Crawl (conditioned)---enclosed crawl/ground"),
                    (241, "Crawl (conditioned)---MF unrated cond space (adiabatic)/ground"),
                    (242, "Crawl (conditioned)---MF unrated heated/ground"),
                    (243, "Crawl (conditioned)---MF buffer/ground"),
                    (244, "Crawl (conditioned)---MF nonfreezing/ground"),
                    (207, "Unconditioned bsmt---ambient/ground"),
                    (208, "Unconditioned bsmt---garage/ground"),
                    (209, "Unconditioned bsmt---open crawl/ground"),
                    (245, "Unconditioned bsmt---MF unrated cond space/ground"),
                    (246, "Unconditioned bsmt---MF unrated heated/ground"),
                    (247, "Unconditioned bsmt---MF buffer/ground"),
                    (248, "Unconditioned bsmt---MF nonfreezing/ground"),
                    (210, "Enclosed crawl---ambient/ground"),
                    (211, "Enclosed crawl---garage/ground"),
                    (212, "Enclosed crawl---open crawl/ground"),
                    (249, "Enclosed crawl---MF unrated cond space/ground"),
                    (250, "Enclosed crawl---MF unrated heated/ground"),
                    (251, "Enclosed crawl---MF buffer/ground"),
                    (252, "Enclosed crawl---MF nonfreezing/ground"),
                ],
                db_column="nFWLoc",
            ),
        ),
        migrations.AlterField(
            model_name="roof",
            name="color",
            field=models.IntegerField(
                choices=[
                    (0, "None"),
                    (1, "Light"),
                    (2, "Medium"),
                    (3, "Dark"),
                    (4, "Reflective"),
                    (5, "Std140"),
                    (6, "Std140-lowAbs"),
                    (7, "White Comp. Shingles"),
                    (8, "White Tile/Concrete"),
                    (9, "White Metal/TPO"),
                ],
                db_column="nROCol",
            ),
        ),
    ]
