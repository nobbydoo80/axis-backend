# Generated by Django 2.2 on 2020-12-03 17:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("customer_hirl", "0103_auto_20201027_1829"),
    ]

    operations = [
        migrations.AlterField(
            model_name="hirlbuilderorganization",
            name="builder_organization",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="company.BuilderOrganization",
            ),
        ),
        migrations.AlterField(
            model_name="hirlraterorganization",
            name="rater_organization",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="company.RaterOrganization",
            ),
        ),
    ]