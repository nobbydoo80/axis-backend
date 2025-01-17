# Generated by Django 4.0.8 on 2022-11-21 14:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_fsm


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("filehandling", "0012_alter_customerdocument_id"),
    ]

    operations = [
        migrations.CreateModel(
            name="RPCService",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("host", models.CharField(max_length=255)),
                ("port", models.IntegerField()),
                (
                    "state",
                    django_fsm.FSMField(
                        choices=[("on", "On"), ("off", "Off")], default="off", max_length=50
                    ),
                ),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="RPCVirtualMachine",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                (
                    "state",
                    django_fsm.FSMField(
                        choices=[("on", "On"), ("off", "Off")], default="off", max_length=50
                    ),
                ),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="RPCSession",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "session_type",
                    models.CharField(
                        choices=[("customer_hirl_updater", "Customer HIRL Updater")], max_length=255
                    ),
                ),
                (
                    "state",
                    django_fsm.FSMField(
                        choices=[
                            ("in_progress", "In Progress"),
                            ("success", "Success"),
                            ("error", "Error"),
                        ],
                        default="in_progress",
                        max_length=50,
                    ),
                ),
                ("finished_at", models.DateTimeField(null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "service",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="rpc.rpcservice"
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="rpcservice",
            name="vm",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="rpc.rpcvirtualmachine"
            ),
        ),
        migrations.CreateModel(
            name="HIRLRPCUpdaterRequest",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "async_document",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="filehandling.asynchronousprocesseddocument",
                    ),
                ),
                (
                    "rpc_session",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="rpc.rpcsession",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
