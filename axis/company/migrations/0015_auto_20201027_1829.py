# Generated by Django 2.2 on 2020-10-27 18:29

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("company", "0014_merge_20200715_1827"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="company",
            name="auto_add_direct_company_relationships",
        ),
        migrations.RemoveField(
            model_name="historicalbuilderorganization",
            name="auto_add_direct_company_relationships",
        ),
        migrations.RemoveField(
            model_name="historicalcompany",
            name="auto_add_direct_company_relationships",
        ),
        migrations.RemoveField(
            model_name="historicaleeporganization",
            name="auto_add_direct_company_relationships",
        ),
        migrations.RemoveField(
            model_name="historicalgeneralorganization",
            name="auto_add_direct_company_relationships",
        ),
        migrations.RemoveField(
            model_name="historicalhvacorganization",
            name="auto_add_direct_company_relationships",
        ),
        migrations.RemoveField(
            model_name="historicalproviderorganization",
            name="auto_add_direct_company_relationships",
        ),
        migrations.RemoveField(
            model_name="historicalqaorganization",
            name="auto_add_direct_company_relationships",
        ),
        migrations.RemoveField(
            model_name="historicalraterorganization",
            name="auto_add_direct_company_relationships",
        ),
        migrations.RemoveField(
            model_name="historicalutilityorganization",
            name="auto_add_direct_company_relationships",
        ),
    ]
