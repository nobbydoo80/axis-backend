# Generated by Django 4.0.6 on 2022-07-22 20:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("customer_hirl", "0206_alter_historicalbuilderagreement_options_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="hirlbuilderorganization",
            name="builder_organization",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="company.company",
            ),
        ),
        migrations.AlterField(
            model_name="hirlprojectarchitect",
            name="architect_organization",
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.CASCADE, to="company.company"
            ),
        ),
        migrations.AlterField(
            model_name="hirlprojectdeveloper",
            name="developer_organization",
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.CASCADE, to="company.company"
            ),
        ),
        migrations.AlterField(
            model_name="hirlprojectowner",
            name="community_owner_organization",
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.CASCADE, to="company.company"
            ),
        ),
        migrations.AlterField(
            model_name="hirlraterorganization",
            name="rater_organization",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="company.company",
            ),
        ),
    ]
