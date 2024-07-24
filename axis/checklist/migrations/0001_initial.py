# Generated by Django 1.11.16 on 2018-10-08 18:15

import axis.checklist.models
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Answer",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("answer", models.TextField()),
                ("comment", models.TextField(blank=True, null=True)),
                ("system_no", models.IntegerField(blank=True, null=True)),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("open", "Open"),
                            ("multiple-choice", "Multiple Choice"),
                            ("date", "Date"),
                            ("datetime", "DateTime"),
                            ("integer", "Whole Number"),
                            ("int", "Whole Number"),
                            ("float", "Decimal Number"),
                            ("csv", "Comma Separated Value"),
                            ("kvfloatcsv", "Key Value (Float) Comma Separated Value"),
                        ],
                        default="open",
                        max_length=50,
                    ),
                ),
                ("photo_required", models.BooleanField(default=False)),
                ("document_required", models.BooleanField(default=False)),
                ("email_required", models.BooleanField(default=False)),
                ("email_sent", models.BooleanField(null=True)),
                ("is_considered_failure", models.BooleanField(default=False)),
                ("display_as_failure", models.BooleanField(default=False)),
                ("failure_is_reviewed", models.BooleanField(default=False)),
                ("confirmed", models.BooleanField(default=False)),
                ("display_flag", models.BooleanField(default=True)),
                ("created_date", models.DateTimeField(editable=False)),
                ("modified_date", models.DateTimeField()),
                ("bulk_uploaded", models.BooleanField(default=False)),
            ],
            options={"verbose_name": "Answer", "verbose_name_plural": "Answers"},
        ),
        migrations.CreateModel(
            name="AnswerDocument",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "document",
                    models.FileField(
                        blank=True,
                        max_length=512,
                        null=True,
                        upload_to=axis.checklist.models._document_location,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="AnswerImage",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "photo",
                    models.FileField(
                        blank=True,
                        max_length=512,
                        null=True,
                        upload_to=axis.checklist.models._photo_location,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="CheckList",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("slug", models.SlugField()),
                ("name", models.CharField(max_length=200)),
                ("public", models.BooleanField(default=True)),
                ("description", models.TextField(blank=True, null=True)),
                ("display_flag", models.BooleanField(default=True)),
                ("created_date", models.DateTimeField(editable=False)),
                ("modified_date", models.DateTimeField()),
            ],
            options={"ordering": ("-created_date",)},
        ),
        migrations.CreateModel(
            name="HistoricalAnswer",
            fields=[
                (
                    "id",
                    models.IntegerField(
                        auto_created=True, blank=True, db_index=True, verbose_name="ID"
                    ),
                ),
                ("answer", models.TextField()),
                ("comment", models.TextField(blank=True, null=True)),
                ("system_no", models.IntegerField(blank=True, null=True)),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("open", "Open"),
                            ("multiple-choice", "Multiple Choice"),
                            ("date", "Date"),
                            ("datetime", "DateTime"),
                            ("integer", "Whole Number"),
                            ("int", "Whole Number"),
                            ("float", "Decimal Number"),
                            ("csv", "Comma Separated Value"),
                            ("kvfloatcsv", "Key Value (Float) Comma Separated Value"),
                        ],
                        default="open",
                        max_length=50,
                    ),
                ),
                ("photo_required", models.BooleanField(default=False)),
                ("document_required", models.BooleanField(default=False)),
                ("email_required", models.BooleanField(default=False)),
                ("email_sent", models.BooleanField(null=True)),
                ("is_considered_failure", models.BooleanField(default=False)),
                ("display_as_failure", models.BooleanField(default=False)),
                ("failure_is_reviewed", models.BooleanField(default=False)),
                ("confirmed", models.BooleanField(default=False)),
                ("display_flag", models.BooleanField(default=True)),
                ("created_date", models.DateTimeField(editable=False)),
                ("modified_date", models.DateTimeField()),
                ("bulk_uploaded", models.BooleanField(default=False)),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                ("history_date", models.DateTimeField()),
                (
                    "history_type",
                    models.CharField(
                        choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")], max_length=1
                    ),
                ),
            ],
            options={
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": "history_date",
                "verbose_name": "historical Answer",
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="HistoricalQAAnswer",
            fields=[
                (
                    "id",
                    models.IntegerField(
                        auto_created=True, blank=True, db_index=True, verbose_name="ID"
                    ),
                ),
                ("answer", models.TextField()),
                ("comment", models.TextField(blank=True, null=True)),
                ("system_no", models.IntegerField(blank=True, null=True)),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("open", "Open"),
                            ("multiple-choice", "Multiple Choice"),
                            ("date", "Date"),
                            ("datetime", "DateTime"),
                            ("integer", "Whole Number"),
                            ("int", "Whole Number"),
                            ("float", "Decimal Number"),
                            ("csv", "Comma Separated Value"),
                            ("kvfloatcsv", "Key Value (Float) Comma Separated Value"),
                        ],
                        default="open",
                        max_length=50,
                    ),
                ),
                ("photo_required", models.BooleanField(default=False)),
                ("document_required", models.BooleanField(default=False)),
                ("email_required", models.BooleanField(default=False)),
                ("email_sent", models.BooleanField(null=True)),
                ("is_considered_failure", models.BooleanField(default=False)),
                ("display_as_failure", models.BooleanField(default=False)),
                ("failure_is_reviewed", models.BooleanField(default=False)),
                ("confirmed", models.BooleanField(default=False)),
                ("display_flag", models.BooleanField(default=True)),
                ("created_date", models.DateTimeField(editable=False)),
                ("modified_date", models.DateTimeField()),
                ("bulk_uploaded", models.BooleanField(default=False)),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                ("history_date", models.DateTimeField()),
                (
                    "history_type",
                    models.CharField(
                        choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")], max_length=1
                    ),
                ),
            ],
            options={
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": "history_date",
                "verbose_name": "historical QA Answer",
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="QAAnswer",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("answer", models.TextField()),
                ("comment", models.TextField(blank=True, null=True)),
                ("system_no", models.IntegerField(blank=True, null=True)),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("open", "Open"),
                            ("multiple-choice", "Multiple Choice"),
                            ("date", "Date"),
                            ("datetime", "DateTime"),
                            ("integer", "Whole Number"),
                            ("int", "Whole Number"),
                            ("float", "Decimal Number"),
                            ("csv", "Comma Separated Value"),
                            ("kvfloatcsv", "Key Value (Float) Comma Separated Value"),
                        ],
                        default="open",
                        max_length=50,
                    ),
                ),
                ("photo_required", models.BooleanField(default=False)),
                ("document_required", models.BooleanField(default=False)),
                ("email_required", models.BooleanField(default=False)),
                ("email_sent", models.BooleanField(null=True)),
                ("is_considered_failure", models.BooleanField(default=False)),
                ("display_as_failure", models.BooleanField(default=False)),
                ("failure_is_reviewed", models.BooleanField(default=False)),
                ("confirmed", models.BooleanField(default=False)),
                ("display_flag", models.BooleanField(default=True)),
                ("created_date", models.DateTimeField(editable=False)),
                ("modified_date", models.DateTimeField()),
                ("bulk_uploaded", models.BooleanField(default=False)),
            ],
            options={
                "verbose_name": "QA Answer",
                "verbose_name_plural": "QA Answers",
            },
        ),
        migrations.CreateModel(
            name="Question",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("priority", models.IntegerField(default=1)),
                ("question", models.TextField(help_text="Enter Question")),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("open", "Open"),
                            ("multiple-choice", "Multiple Choice"),
                            ("date", "Date"),
                            ("datetime", "DateTime"),
                            ("integer", "Whole Number"),
                            ("int", "Whole Number"),
                            ("float", "Decimal Number"),
                            ("csv", "Comma Separated Value"),
                            ("kvfloatcsv", "Key Value (Float) Comma Separated Value"),
                        ],
                        default="open",
                        help_text="Select type of Question",
                        max_length=100,
                    ),
                ),
                (
                    "description",
                    models.TextField(blank=True, help_text="Enter Question Description", null=True),
                ),
                ("help_url", models.CharField(blank=True, max_length=512, null=True)),
                ("unit", models.CharField(blank=True, max_length=50, null=True)),
                ("allow_bulk_fill", models.BooleanField(default=False)),
                ("is_optional", models.BooleanField(default=False)),
                ("minimum_value", models.FloatField(blank=True, default=None, null=True)),
                ("maximum_value", models.FloatField(blank=True, default=None, null=True)),
                ("display_flag", models.BooleanField(default=True)),
                ("created_date", models.DateTimeField(editable=False)),
                ("modified_date", models.DateTimeField()),
                ("slug", models.SlugField(editable=False, unique=True)),
            ],
            options={
                "ordering": ("priority", "question"),
            },
        ),
        migrations.CreateModel(
            name="QuestionChoice",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("choice", models.CharField(max_length=255)),
                ("photo_required", models.BooleanField(default=False)),
                ("document_required", models.BooleanField(default=False)),
                ("email_required", models.BooleanField(default=False)),
                ("comment_required", models.BooleanField(default=False)),
                ("is_considered_failure", models.BooleanField(default=False)),
                ("display_as_failure", models.BooleanField(default=False)),
                ("choice_order", models.IntegerField()),
                ("display_flag", models.BooleanField(default=True)),
                ("created_date", models.DateTimeField(editable=False)),
                ("modified_date", models.DateTimeField()),
            ],
            options={
                "ordering": ("choice_order",),
            },
        ),
        migrations.CreateModel(
            name="Section",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("slug", models.SlugField(max_length=255, unique=True)),
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True, null=True)),
                ("priority", models.IntegerField(default=1)),
                ("display_flag", models.BooleanField(default=True)),
                ("created_date", models.DateTimeField(editable=False)),
                ("modified_date", models.DateTimeField()),
                (
                    "checklist",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="checklist.CheckList",
                    ),
                ),
                ("questions", models.ManyToManyField(to="checklist.Question")),
            ],
            options={
                "ordering": ("priority",),
            },
        ),
    ]