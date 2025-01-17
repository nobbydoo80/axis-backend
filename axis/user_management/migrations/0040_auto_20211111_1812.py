# Generated by Django 3.2.9 on 2021-11-11 18:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("user_management", "0039_alter_accreditation_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="accreditation",
            name="approver",
            field=models.ForeignKey(
                help_text="User who approved this accreditation",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="approved_accreditations",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="accreditation",
            name="trainee",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="accreditations",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
