# Generated by Django 1.11.16 on 2018-10-08 18:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("customer_hirl", "0001_initial"),
        ("home", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="certification",
            name="candidates",
            field=models.ManyToManyField(
                blank=True,
                related_name="hirl_certification_candidates",
                through="customer_hirl.Candidate",
                to="home.Home",
            ),
        ),
        migrations.AddField(
            model_name="certification",
            name="home",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="hirl_certification",
                to="home.Home",
            ),
        ),
        migrations.AddField(
            model_name="candidate",
            name="certification",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="customer_hirl.Certification"
            ),
        ),
        migrations.AddField(
            model_name="candidate",
            name="home",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="home.Home"),
        ),
    ]
