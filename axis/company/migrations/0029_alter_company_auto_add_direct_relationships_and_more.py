# Generated by Django 4.0.6 on 2022-08-18 17:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("geographic", "0006_auto_20220719_1459"),
        ("auth", "0012_alter_user_first_name_max_length"),
        ("company", "0028_auto_20220726_1908"),
    ]

    operations = [
        migrations.AlterField(
            model_name="company",
            name="auto_add_direct_relationships",
            field=models.BooleanField(
                default=True,
                help_text="Enabling this will allow any company that wants you to have a relationship with another object (i.e. subdivision, home, floorplan, etc) to automatically be accepted.",
            ),
        ),
        migrations.AlterField(
            model_name="historicalarchitectorganization",
            name="auto_add_direct_relationships",
            field=models.BooleanField(
                default=True,
                help_text="Enabling this will allow any company that wants you to have a relationship with another object (i.e. subdivision, home, floorplan, etc) to automatically be accepted.",
            ),
        ),
        migrations.AlterField(
            model_name="historicalbuilderorganization",
            name="auto_add_direct_relationships",
            field=models.BooleanField(
                default=True,
                help_text="Enabling this will allow any company that wants you to have a relationship with another object (i.e. subdivision, home, floorplan, etc) to automatically be accepted.",
            ),
        ),
        migrations.AlterField(
            model_name="historicalcommunityownerorganization",
            name="auto_add_direct_relationships",
            field=models.BooleanField(
                default=True,
                help_text="Enabling this will allow any company that wants you to have a relationship with another object (i.e. subdivision, home, floorplan, etc) to automatically be accepted.",
            ),
        ),
        migrations.AlterField(
            model_name="historicalcompany",
            name="auto_add_direct_relationships",
            field=models.BooleanField(
                default=True,
                help_text="Enabling this will allow any company that wants you to have a relationship with another object (i.e. subdivision, home, floorplan, etc) to automatically be accepted.",
            ),
        ),
        migrations.AlterField(
            model_name="historicaldeveloperorganization",
            name="auto_add_direct_relationships",
            field=models.BooleanField(
                default=True,
                help_text="Enabling this will allow any company that wants you to have a relationship with another object (i.e. subdivision, home, floorplan, etc) to automatically be accepted.",
            ),
        ),
        migrations.AlterField(
            model_name="historicaleeporganization",
            name="auto_add_direct_relationships",
            field=models.BooleanField(
                default=True,
                help_text="Enabling this will allow any company that wants you to have a relationship with another object (i.e. subdivision, home, floorplan, etc) to automatically be accepted.",
            ),
        ),
        migrations.AlterField(
            model_name="historicalgeneralorganization",
            name="auto_add_direct_relationships",
            field=models.BooleanField(
                default=True,
                help_text="Enabling this will allow any company that wants you to have a relationship with another object (i.e. subdivision, home, floorplan, etc) to automatically be accepted.",
            ),
        ),
        migrations.AlterField(
            model_name="historicalhvacorganization",
            name="auto_add_direct_relationships",
            field=models.BooleanField(
                default=True,
                help_text="Enabling this will allow any company that wants you to have a relationship with another object (i.e. subdivision, home, floorplan, etc) to automatically be accepted.",
            ),
        ),
        migrations.AlterField(
            model_name="historicalproviderorganization",
            name="auto_add_direct_relationships",
            field=models.BooleanField(
                default=True,
                help_text="Enabling this will allow any company that wants you to have a relationship with another object (i.e. subdivision, home, floorplan, etc) to automatically be accepted.",
            ),
        ),
        migrations.AlterField(
            model_name="historicalqaorganization",
            name="auto_add_direct_relationships",
            field=models.BooleanField(
                default=True,
                help_text="Enabling this will allow any company that wants you to have a relationship with another object (i.e. subdivision, home, floorplan, etc) to automatically be accepted.",
            ),
        ),
        migrations.AlterField(
            model_name="historicalraterorganization",
            name="auto_add_direct_relationships",
            field=models.BooleanField(
                default=True,
                help_text="Enabling this will allow any company that wants you to have a relationship with another object (i.e. subdivision, home, floorplan, etc) to automatically be accepted.",
            ),
        ),
        migrations.AlterField(
            model_name="historicalutilityorganization",
            name="auto_add_direct_relationships",
            field=models.BooleanField(
                default=True,
                help_text="Enabling this will allow any company that wants you to have a relationship with another object (i.e. subdivision, home, floorplan, etc) to automatically be accepted.",
            ),
        ),
    ]
