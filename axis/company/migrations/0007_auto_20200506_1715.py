# Generated by Django 1.11.26 on 2020-05-06 17:15

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("company", "0006_auto_20200506_1654"),
    ]

    operations = [
        migrations.AlterField(
            model_name="company",
            name="insurance_certificate",
            field=models.FileField(max_length=512, null=True, upload_to=b""),
        ),
        migrations.AlterField(
            model_name="historicalbuilderorganization",
            name="insurance_certificate",
            field=models.TextField(max_length=512, null=True),
        ),
        migrations.AlterField(
            model_name="historicalcompany",
            name="insurance_certificate",
            field=models.TextField(max_length=512, null=True),
        ),
        migrations.AlterField(
            model_name="historicaleeporganization",
            name="insurance_certificate",
            field=models.TextField(max_length=512, null=True),
        ),
        migrations.AlterField(
            model_name="historicalgeneralorganization",
            name="insurance_certificate",
            field=models.TextField(max_length=512, null=True),
        ),
        migrations.AlterField(
            model_name="historicalhvacorganization",
            name="insurance_certificate",
            field=models.TextField(max_length=512, null=True),
        ),
        migrations.AlterField(
            model_name="historicalproviderorganization",
            name="insurance_certificate",
            field=models.TextField(max_length=512, null=True),
        ),
        migrations.AlterField(
            model_name="historicalqaorganization",
            name="insurance_certificate",
            field=models.TextField(max_length=512, null=True),
        ),
        migrations.AlterField(
            model_name="historicalraterorganization",
            name="insurance_certificate",
            field=models.TextField(max_length=512, null=True),
        ),
        migrations.AlterField(
            model_name="historicalutilityorganization",
            name="insurance_certificate",
            field=models.TextField(max_length=512, null=True),
        ),
    ]
