# Generated by Django 1.11.26 on 2020-07-22 12:15

import django.db.models.deletion
import phonenumber_field.modelfields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("company", "0014_merge_20200715_1827"),
        ("eep_program", "0017_auto_20200312_1323"),
        ("geocoder", "0011_merge_20200701_0829"),
        ("customer_hirl", "0064_auto_20200708_1011"),
    ]

    operations = [
        migrations.CreateModel(
            name="HIRLGreenEnergyBadge",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("slug", models.SlugField(max_length=255)),
            ],
            options={
                "verbose_name": "Green Energy Badge",
                "verbose_name_plural": "Green Energy Badges",
            },
        ),
        migrations.AddField(
            model_name="hirlproject",
            name="accessory_structure_description",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="hirlproject",
            name="builder",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="company.BuilderOrganization",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="hirlproject",
            name="builder_email",
            field=models.CharField(blank=True, max_length=65),
        ),
        migrations.AddField(
            model_name="hirlproject",
            name="builder_first_name",
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name="hirlproject",
            name="builder_last_name",
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name="hirlproject",
            name="builder_phone_number",
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name="hirlproject",
            name="eep_program",
            field=models.ForeignKey(
                default=1, on_delete=django.db.models.deletion.CASCADE, to="eep_program.EEPProgram"
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="hirlproject",
            name="is_associated_with_accessory_structure_seeking_certification",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="hirlproject",
            name="project_geocode",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="geocoder.Geocode",
            ),
        ),
        migrations.AddField(
            model_name="hirlproject",
            name="project_type",
            field=models.PositiveSmallIntegerField(
                choices=[(1, "Single Family"), (2, "Multi Family")], default=1
            ),
        ),
        migrations.AddField(
            model_name="hirlproject",
            name="rough_inspection_schedule",
            field=models.PositiveSmallIntegerField(
                choices=[(0, "Any date"), (1, "Rough inspection planned within the next 5 days")],
                default=0,
            ),
        ),
        migrations.AddField(
            model_name="historicalhirlproject",
            name="accessory_structure_description",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="historicalhirlproject",
            name="builder",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="company.BuilderOrganization",
            ),
        ),
        migrations.AddField(
            model_name="historicalhirlproject",
            name="builder_email",
            field=models.CharField(blank=True, max_length=65),
        ),
        migrations.AddField(
            model_name="historicalhirlproject",
            name="builder_first_name",
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name="historicalhirlproject",
            name="builder_last_name",
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name="historicalhirlproject",
            name="builder_phone_number",
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name="historicalhirlproject",
            name="eep_program",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="eep_program.EEPProgram",
            ),
        ),
        migrations.AddField(
            model_name="historicalhirlproject",
            name="is_associated_with_accessory_structure_seeking_certification",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="historicalhirlproject",
            name="project_geocode",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="geocoder.Geocode",
            ),
        ),
        migrations.AddField(
            model_name="historicalhirlproject",
            name="project_type",
            field=models.PositiveSmallIntegerField(
                choices=[(1, "Single Family"), (2, "Multi Family")], default=1
            ),
        ),
        migrations.AddField(
            model_name="historicalhirlproject",
            name="rough_inspection_schedule",
            field=models.PositiveSmallIntegerField(
                choices=[(0, "Any date"), (1, "Rough inspection planned within the next 5 days")],
                default=0,
            ),
        ),
        migrations.AddField(
            model_name="hirlproject",
            name="green_energy_badges",
            field=models.ManyToManyField(to="customer_hirl.HIRLGreenEnergyBadge"),
        ),
    ]
