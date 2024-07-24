# Generated by Django 1.11.26 on 2019-12-11 14:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("company", "0004_auto_20190826_2024"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("user_management", "0010_auto_20191210_1757"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="accreditationstatus",
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name="accreditationstatus",
            name="accreditation",
        ),
        migrations.RemoveField(
            model_name="accreditationstatus",
            name="approver",
        ),
        migrations.RemoveField(
            model_name="accreditationstatus",
            name="company",
        ),
        migrations.RemoveField(
            model_name="historicalaccreditationstatus",
            name="accreditation",
        ),
        migrations.RemoveField(
            model_name="historicalaccreditationstatus",
            name="approver",
        ),
        migrations.RemoveField(
            model_name="historicalaccreditationstatus",
            name="company",
        ),
        migrations.RemoveField(
            model_name="historicalaccreditationstatus",
            name="history_user",
        ),
        migrations.RemoveField(
            model_name="accreditation",
            name="statuses",
        ),
        migrations.AddField(
            model_name="accreditation",
            name="approver",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="accreditation_approvers",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="accreditation",
            name="oversight_company",
            field=models.ForeignKey(
                default=1, on_delete=django.db.models.deletion.CASCADE, to="company.Company"
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="accreditation",
            name="state",
            field=models.SmallIntegerField(
                choices=[
                    (1, "Inactive"),
                    (2, "Active"),
                    (3, "Probation \u2013 New"),
                    (4, "Probation \u2013 Disciplinary"),
                    (5, "Suspended \u2013 Administrative"),
                    (6, "Suspended \u2013 Disciplinary"),
                    (7, "Terminated \u2013 Administrative"),
                    (8, "Terminated \u2013 Disciplinary (Revoked)"),
                ],
                default=1,
            ),
        ),
        migrations.AddField(
            model_name="accreditation",
            name="state_changed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="accreditation",
            name="trainee",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="accreditation_trainees",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.DeleteModel(
            name="AccreditationStatus",
        ),
        migrations.DeleteModel(
            name="HistoricalAccreditationStatus",
        ),
    ]
