# Generated by Django 3.1.3 on 2021-01-04 19:42

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("company", "0020_auto_20210104_1851"),
    ]

    operations = [
        migrations.AlterField(
            model_name="company",
            name="company_type",
            field=models.CharField(
                choices=[
                    ("builder", "Builder"),
                    ("eep", "Program Sponsor"),
                    ("provider", "Rating Provider"),
                    ("rater", "Rating Company"),
                    ("utility", "Utility Company"),
                    ("hvac", "HVAC Contractor"),
                    ("qa", "QA/QC Company"),
                    ("general", "General Company"),
                    ("architect", "Architect Company"),
                    ("developer", "Developer Company"),
                    ("communityowner", "Owner Company"),
                ],
                max_length=32,
            ),
        ),
        migrations.AlterField(
            model_name="historicalarchitectorganization",
            name="company_type",
            field=models.CharField(
                choices=[
                    ("builder", "Builder"),
                    ("eep", "Program Sponsor"),
                    ("provider", "Rating Provider"),
                    ("rater", "Rating Company"),
                    ("utility", "Utility Company"),
                    ("hvac", "HVAC Contractor"),
                    ("qa", "QA/QC Company"),
                    ("general", "General Company"),
                    ("architect", "Architect Company"),
                    ("developer", "Developer Company"),
                    ("communityowner", "Owner Company"),
                ],
                max_length=32,
            ),
        ),
        migrations.AlterField(
            model_name="historicalbuilderorganization",
            name="company_type",
            field=models.CharField(
                choices=[
                    ("builder", "Builder"),
                    ("eep", "Program Sponsor"),
                    ("provider", "Rating Provider"),
                    ("rater", "Rating Company"),
                    ("utility", "Utility Company"),
                    ("hvac", "HVAC Contractor"),
                    ("qa", "QA/QC Company"),
                    ("general", "General Company"),
                    ("architect", "Architect Company"),
                    ("developer", "Developer Company"),
                    ("communityowner", "Owner Company"),
                ],
                max_length=32,
            ),
        ),
        migrations.AlterField(
            model_name="historicalcommunityownerorganization",
            name="company_type",
            field=models.CharField(
                choices=[
                    ("builder", "Builder"),
                    ("eep", "Program Sponsor"),
                    ("provider", "Rating Provider"),
                    ("rater", "Rating Company"),
                    ("utility", "Utility Company"),
                    ("hvac", "HVAC Contractor"),
                    ("qa", "QA/QC Company"),
                    ("general", "General Company"),
                    ("architect", "Architect Company"),
                    ("developer", "Developer Company"),
                    ("communityowner", "Owner Company"),
                ],
                max_length=32,
            ),
        ),
        migrations.AlterField(
            model_name="historicalcompany",
            name="company_type",
            field=models.CharField(
                choices=[
                    ("builder", "Builder"),
                    ("eep", "Program Sponsor"),
                    ("provider", "Rating Provider"),
                    ("rater", "Rating Company"),
                    ("utility", "Utility Company"),
                    ("hvac", "HVAC Contractor"),
                    ("qa", "QA/QC Company"),
                    ("general", "General Company"),
                    ("architect", "Architect Company"),
                    ("developer", "Developer Company"),
                    ("communityowner", "Owner Company"),
                ],
                max_length=32,
            ),
        ),
        migrations.AlterField(
            model_name="historicaldeveloperorganization",
            name="company_type",
            field=models.CharField(
                choices=[
                    ("builder", "Builder"),
                    ("eep", "Program Sponsor"),
                    ("provider", "Rating Provider"),
                    ("rater", "Rating Company"),
                    ("utility", "Utility Company"),
                    ("hvac", "HVAC Contractor"),
                    ("qa", "QA/QC Company"),
                    ("general", "General Company"),
                    ("architect", "Architect Company"),
                    ("developer", "Developer Company"),
                    ("communityowner", "Owner Company"),
                ],
                max_length=32,
            ),
        ),
        migrations.AlterField(
            model_name="historicaleeporganization",
            name="company_type",
            field=models.CharField(
                choices=[
                    ("builder", "Builder"),
                    ("eep", "Program Sponsor"),
                    ("provider", "Rating Provider"),
                    ("rater", "Rating Company"),
                    ("utility", "Utility Company"),
                    ("hvac", "HVAC Contractor"),
                    ("qa", "QA/QC Company"),
                    ("general", "General Company"),
                    ("architect", "Architect Company"),
                    ("developer", "Developer Company"),
                    ("communityowner", "Owner Company"),
                ],
                max_length=32,
            ),
        ),
        migrations.AlterField(
            model_name="historicalgeneralorganization",
            name="company_type",
            field=models.CharField(
                choices=[
                    ("builder", "Builder"),
                    ("eep", "Program Sponsor"),
                    ("provider", "Rating Provider"),
                    ("rater", "Rating Company"),
                    ("utility", "Utility Company"),
                    ("hvac", "HVAC Contractor"),
                    ("qa", "QA/QC Company"),
                    ("general", "General Company"),
                    ("architect", "Architect Company"),
                    ("developer", "Developer Company"),
                    ("communityowner", "Owner Company"),
                ],
                max_length=32,
            ),
        ),
        migrations.AlterField(
            model_name="historicalhvacorganization",
            name="company_type",
            field=models.CharField(
                choices=[
                    ("builder", "Builder"),
                    ("eep", "Program Sponsor"),
                    ("provider", "Rating Provider"),
                    ("rater", "Rating Company"),
                    ("utility", "Utility Company"),
                    ("hvac", "HVAC Contractor"),
                    ("qa", "QA/QC Company"),
                    ("general", "General Company"),
                    ("architect", "Architect Company"),
                    ("developer", "Developer Company"),
                    ("communityowner", "Owner Company"),
                ],
                max_length=32,
            ),
        ),
        migrations.AlterField(
            model_name="historicalproviderorganization",
            name="company_type",
            field=models.CharField(
                choices=[
                    ("builder", "Builder"),
                    ("eep", "Program Sponsor"),
                    ("provider", "Rating Provider"),
                    ("rater", "Rating Company"),
                    ("utility", "Utility Company"),
                    ("hvac", "HVAC Contractor"),
                    ("qa", "QA/QC Company"),
                    ("general", "General Company"),
                    ("architect", "Architect Company"),
                    ("developer", "Developer Company"),
                    ("communityowner", "Owner Company"),
                ],
                max_length=32,
            ),
        ),
        migrations.AlterField(
            model_name="historicalqaorganization",
            name="company_type",
            field=models.CharField(
                choices=[
                    ("builder", "Builder"),
                    ("eep", "Program Sponsor"),
                    ("provider", "Rating Provider"),
                    ("rater", "Rating Company"),
                    ("utility", "Utility Company"),
                    ("hvac", "HVAC Contractor"),
                    ("qa", "QA/QC Company"),
                    ("general", "General Company"),
                    ("architect", "Architect Company"),
                    ("developer", "Developer Company"),
                    ("communityowner", "Owner Company"),
                ],
                max_length=32,
            ),
        ),
        migrations.AlterField(
            model_name="historicalraterorganization",
            name="company_type",
            field=models.CharField(
                choices=[
                    ("builder", "Builder"),
                    ("eep", "Program Sponsor"),
                    ("provider", "Rating Provider"),
                    ("rater", "Rating Company"),
                    ("utility", "Utility Company"),
                    ("hvac", "HVAC Contractor"),
                    ("qa", "QA/QC Company"),
                    ("general", "General Company"),
                    ("architect", "Architect Company"),
                    ("developer", "Developer Company"),
                    ("communityowner", "Owner Company"),
                ],
                max_length=32,
            ),
        ),
        migrations.AlterField(
            model_name="historicalutilityorganization",
            name="company_type",
            field=models.CharField(
                choices=[
                    ("builder", "Builder"),
                    ("eep", "Program Sponsor"),
                    ("provider", "Rating Provider"),
                    ("rater", "Rating Company"),
                    ("utility", "Utility Company"),
                    ("hvac", "HVAC Contractor"),
                    ("qa", "QA/QC Company"),
                    ("general", "General Company"),
                    ("architect", "Architect Company"),
                    ("developer", "Developer Company"),
                    ("communityowner", "Owner Company"),
                ],
                max_length=32,
            ),
        ),
    ]
