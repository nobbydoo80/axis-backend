# Generated by Django 1.11.17 on 2019-05-25 22:35

import axis.builder_agreement.models
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("builder_agreement", "0008_auto_20190530_1854"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="builderagreementdocument",
            name="builder_agreement",
        ),
        migrations.RemoveField(
            model_name="builderagreementdocument",
            name="company",
        ),
        migrations.RemoveField(
            model_name="historicalbuilderagreementdocument",
            name="builder_agreement",
        ),
        migrations.RemoveField(
            model_name="historicalbuilderagreementdocument",
            name="company",
        ),
        migrations.RemoveField(
            model_name="historicalbuilderagreementdocument",
            name="history_user",
        ),
        migrations.RemoveField(
            model_name="builderagreement",
            name="documents",
        ),
        migrations.AlterField(
            model_name="builderagreement",
            name="document",
            field=models.FileField(
                blank=True,
                help_text="The hard copy of the builder agreement.",
                max_length=512,
                null=True,
                upload_to=axis.builder_agreement.models.builder_agreement_file_name,
            ),
        ),
        migrations.AlterField(
            model_name="historicalbuilderagreement",
            name="document",
            field=models.TextField(
                blank=True,
                help_text="The hard copy of the builder agreement.",
                max_length=512,
                null=True,
            ),
        ),
        migrations.DeleteModel(
            name="BuilderAgreementDocument",
        ),
        migrations.DeleteModel(
            name="HistoricalBuilderAgreementDocument",
        ),
    ]
