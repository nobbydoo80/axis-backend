# Generated by Django 4.0.8 on 2022-12-07 18:36

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("rpc", "0005_hirlrpcupdaterrequest_result"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="hirlrpcupdaterrequest",
            options={"ordering": ("-created_at",)},
        ),
        migrations.AlterModelOptions(
            name="rpcservice",
            options={"ordering": ("-created_at",)},
        ),
        migrations.AlterModelOptions(
            name="rpcsession",
            options={"ordering": ("-created_at",)},
        ),
        migrations.AlterModelOptions(
            name="rpcvirtualmachine",
            options={"ordering": ("-created_at",), "verbose_name": "Virtual Machine"},
        ),
    ]