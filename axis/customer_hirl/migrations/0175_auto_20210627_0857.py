# Generated by Django 3.2.4 on 2021-06-27 08:57

import hashid_field.field
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("customer_hirl", "0174_hirlverifiercertificationbadgestorecords"),
    ]

    operations = [
        migrations.AlterField(
            model_name="builderagreement",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="candidate",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="coidocument",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="hirlbuilderagreementstatus",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="hirlbuilderinsurance",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="hirlbuilderorganization",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="hirlgreenenergybadge",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="hirllegacycertification",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="hirllegacyregistration",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="hirlproject",
            name="id",
            field=hashid_field.field.HashidAutoField(
                alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890",
                min_length=7,
                prefix="",
                primary_key=True,
                serialize=False,
            ),
        ),
        migrations.AlterField(
            model_name="hirlprojectarchitect",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="hirlprojectcontact",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="hirlprojectdeveloper",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="hirlprojectowner",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="hirlprojectregistration",
            name="id",
            field=hashid_field.field.HashidAutoField(
                alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890",
                min_length=7,
                prefix="",
                primary_key=True,
                serialize=False,
            ),
        ),
        migrations.AlterField(
            model_name="hirlraterorganization",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="hirlrateruser",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="hirluserprofile",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="hirlverifieraccreditationstatus",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="hirlverifieragreementstatus",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="hirlverifiercertificationbadgestorecords",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="hirlverifiercommunityproject",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="hirlverifierinsurance",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="historicalbuilderagreement",
            name="id",
            field=models.BigIntegerField(
                auto_created=True, blank=True, db_index=True, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="historicalcoidocument",
            name="id",
            field=models.BigIntegerField(
                auto_created=True, blank=True, db_index=True, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="historicalhirlgreenenergybadge",
            name="id",
            field=models.BigIntegerField(
                auto_created=True, blank=True, db_index=True, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="historicalhirlproject",
            name="id",
            field=models.IntegerField(blank=True, db_index=True),
        ),
        migrations.AlterField(
            model_name="historicalhirlprojectregistration",
            name="id",
            field=models.IntegerField(blank=True, db_index=True),
        ),
        migrations.AlterField(
            model_name="historicalverifieragreement",
            name="id",
            field=models.BigIntegerField(
                auto_created=True, blank=True, db_index=True, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="providedservice",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="verifieragreement",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
    ]