# Generated by Django 1.11.16 on 2018-10-10 23:16

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("company", "0002_auto_20181008_1815"),
    ]

    operations = [
        migrations.AddField(
            model_name="historicalaltname",
            name="history_change_reason",
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="historicalbuilderorganization",
            name="history_change_reason",
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="historicalcompany",
            name="history_change_reason",
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="historicalcompanydocument",
            name="history_change_reason",
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="historicaleeporganization",
            name="history_change_reason",
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="historicalgeneralorganization",
            name="history_change_reason",
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="historicalhvacorganization",
            name="history_change_reason",
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="historicalproviderorganization",
            name="history_change_reason",
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="historicalqaorganization",
            name="history_change_reason",
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="historicalraterorganization",
            name="history_change_reason",
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="historicalutilityorganization",
            name="history_change_reason",
            field=models.CharField(max_length=100, null=True),
        ),
    ]
