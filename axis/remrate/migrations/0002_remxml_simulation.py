from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("remrate", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="remxml",
            options={
                "verbose_name": "REM/Rate XML Conversion",
            },
        ),
        migrations.RenameField(
            model_name="remxml",
            old_name="blg_version",
            new_name="source_version",
        ),
        migrations.AddField(
            model_name="remxml",
            name="source_type",
            field=models.CharField(
                default="blg_file",
                max_length=16,
                choices=[("blg_file", "BLG File"), ("simulation", "REM/Rate Export")],
            ),
            preserve_default=False,
        ),
    ]
