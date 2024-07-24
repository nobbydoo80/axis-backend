__author__ = "Steven K"
__date__ = "04/21/2023 8:06 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]


from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Table

from rest_framework import serializers

from axis.customer_eto.api_v3.fields import CappedCommaFloatField
from axis.customer_eto.enumerations import HeatType
from axis.customer_eto.models import FastTrackSubmission


class HomeProjectETO2022IncentiveSerializer(serializers.ModelSerializer):
    """This is the incentive section of a project report for ETO."""

    id = serializers.IntegerField()

    savings_kwh = CappedCommaFloatField(
        default=0, round_value=2, minimum_acceptable_value=0, source="kwh_savings"
    )
    savings_therms = CappedCommaFloatField(
        default=0, round_value=2, minimum_acceptable_value=0, source="therm_savings"
    )
    percent_improvement = CappedCommaFloatField(
        default=0,
        round_value=2,
        minimum_acceptable_value=0,
        represent_percent=True,
    )
    builder_incentive = CappedCommaFloatField(
        prefix="$", default=0, round_value=2, minimum_acceptable_value=0
    )
    builder_electric_incentive = CappedCommaFloatField(
        prefix="$", default=0, round_value=2, minimum_acceptable_value=0
    )
    builder_gas_incentive = CappedCommaFloatField(
        prefix="$", default=0, round_value=2, minimum_acceptable_value=0
    )
    rater_incentive = CappedCommaFloatField(
        prefix="$", default=0, round_value=2, minimum_acceptable_value=0
    )
    rater_electric_incentive = CappedCommaFloatField(
        prefix="$", default=0, round_value=2, minimum_acceptable_value=0
    )
    rater_gas_incentive = CappedCommaFloatField(
        prefix="$", default=0, round_value=2, minimum_acceptable_value=0
    )
    # ONLY ENH
    ev_ready_builder_incentive = CappedCommaFloatField(
        prefix="$", default=0, round_value=2, minimum_acceptable_value=0
    )

    # ONLY SLE
    net_zero_solar_incentive = CappedCommaFloatField(
        prefix="$", default=0, round_value=2, minimum_acceptable_value=0
    )
    solar_ready_builder_incentive = CappedCommaFloatField(
        prefix="$", default=0, round_value=2, minimum_acceptable_value=0
    )
    solar_ready_verifier_incentive = CappedCommaFloatField(
        prefix="$", default=0, round_value=2, minimum_acceptable_value=0
    )
    solar_storage_builder_incentive = CappedCommaFloatField(
        prefix="$", default=0, round_value=2, minimum_acceptable_value=0
    )

    heat_type = serializers.ChoiceField(
        choices=[HeatType.GAS, HeatType.ELECTRIC],
        required=False,
    )

    cobid_builder_incentive = CappedCommaFloatField(
        prefix="$",
        default=0,
        round_value=2,
        minimum_acceptable_value=0,
    )
    triple_pane_window_incentive = CappedCommaFloatField(
        prefix="$", default=0, round_value=2, minimum_acceptable_value=0
    )
    rigid_insulation_incentive = CappedCommaFloatField(
        prefix="$", default=0, round_value=2, minimum_acceptable_value=0
    )
    sealed_attic_incentive = CappedCommaFloatField(
        prefix="$", default=0, round_value=2, minimum_acceptable_value=0
    )

    # Variable
    heat_pump_water_heater_electric_incentive = CappedCommaFloatField(
        prefix="$",
        default=0,
        round_value=2,
        maximum_acceptable_value=0,
        represent_negatives_as_paren=True,
        source="builder_heat_pump_water_heater_electric_incentive",
    )
    heat_pump_water_heater_gas_incentive = CappedCommaFloatField(
        prefix="$",
        default=0,
        round_value=2,
        maximum_acceptable_value=0,
        represent_negatives_as_paren=True,
        source="builder_heat_pump_water_heater_gas_incentive",
    )
    heat_pump_water_heater_incentive = CappedCommaFloatField(
        prefix="$",
        default=0,
        round_value=2,
        maximum_acceptable_value=0,
        represent_negatives_as_paren=True,
    )
    builder_electric_baseline = CappedCommaFloatField(
        prefix="$",
        default=0,
        round_value=2,
        minimum_acceptable_value=0,
        source="builder_electric_baseline_incentive",
    )

    builder_gas_baseline = CappedCommaFloatField(
        prefix="$",
        default=0,
        round_value=2,
        minimum_acceptable_value=0,
        source="builder_gas_baseline_incentive",
    )

    builder_sle_total = CappedCommaFloatField(
        prefix="$",
        default=0,
        round_value=2,
        minimum_acceptable_value=0,
        source="total_builder_sle_incentive",
    )
    total_builder_incentive = CappedCommaFloatField(
        prefix="$",
        default=0,
        round_value=2,
        minimum_acceptable_value=0,
    )

    cobid_verifier_incentive = CappedCommaFloatField(
        prefix="$", default=0, round_value=2, minimum_acceptable_value=0
    )
    solar_ready_verifier_incentive = CappedCommaFloatField(
        prefix="$", default=0, round_value=2, minimum_acceptable_value=0
    )
    rater_electric_baseline = CappedCommaFloatField(
        prefix="$",
        default=0,
        round_value=2,
        minimum_acceptable_value=0,
        source="rater_electric_baseline_incentive",
    )

    rater_gas_baseline = CappedCommaFloatField(
        prefix="$",
        default=0,
        round_value=2,
        minimum_acceptable_value=0,
        source="rater_gas_baseline_incentive",
    )

    rater_sle_total = CappedCommaFloatField(
        prefix="$",
        default=0,
        round_value=2,
        minimum_acceptable_value=0,
        source="total_rater_sle_incentive",
    )
    total_rater_incentive = CappedCommaFloatField(
        prefix="$",
        default=0,
        round_value=2,
        minimum_acceptable_value=0,
    )

    class Meta:
        model = FastTrackSubmission
        fields = (
            "id",
            "savings_kwh",
            "savings_therms",
            "percent_improvement",
            "builder_incentive",
            "builder_electric_baseline",
            "builder_electric_incentive",
            "builder_gas_baseline",
            "builder_gas_incentive",
            "total_builder_incentive",
            "total_rater_incentive",
            "rater_incentive",
            "rater_electric_baseline",
            "rater_gas_baseline",
            "rater_electric_incentive",
            "rater_gas_incentive",
            "ev_ready_builder_incentive",
            "net_zero_solar_incentive",
            "solar_ready_builder_incentive",
            "solar_ready_verifier_incentive",
            "solar_storage_builder_incentive",
            "heat_type",
            "cobid_builder_incentive",
            "heat_pump_water_heater_incentive",
            "heat_pump_water_heater_electric_incentive",
            "heat_pump_water_heater_gas_incentive",
            "triple_pane_window_incentive",
            "rigid_insulation_incentive",
            "sealed_attic_incentive",
            "builder_sle_total",
            # Verifier
            "cobid_verifier_incentive",
            "solar_ready_verifier_incentive",
            "rater_sle_total",
        )

    def get_detail_table(self, **attrs: dict) -> list:
        # This dumps out the representative table data
        nbsp = "&nbsp;"
        data = [
            [
                "<b><u>Builder Detailed Incentives</u></b>",
                "<b><u>ENH Electric</u></b>",
                "<b><u>ENH Gas</u></b>",
                "<b><u>SLE</u></b>",
            ],
            [
                "Builder Performance Incentive",
                attrs["builder_electric_baseline"],
                attrs["builder_gas_baseline"],
                nbsp,
            ],
            ["Net Zero", nbsp, nbsp, attrs["net_zero_solar_incentive"]],
            ["Builder Solar Ready", nbsp, nbsp, attrs["solar_ready_builder_incentive"]],
            ["EV Ready", attrs["ev_ready_builder_incentive"], nbsp, nbsp],
            ["ESH Solar + Storage", nbsp, nbsp, attrs["solar_storage_builder_incentive"]],
            ["Builder DEI", nbsp, nbsp, nbsp],
            [
                "HPWH Deduction",
                attrs["heat_pump_water_heater_electric_incentive"]
                if attrs["heat_pump_water_heater_electric_incentive"] != "$0.00"
                else nbsp,
                attrs["heat_pump_water_heater_gas_incentive"]
                if attrs["heat_pump_water_heater_gas_incentive"] != "$0.00"
                else nbsp,
                nbsp,
            ],
            ["Fire Rebuild- Triple Pane Windows", nbsp, nbsp, nbsp],
            ["Fire Rebuild- Exterior Rigid Insulation", nbsp, nbsp, nbsp],
            ["Fire Rebuild- Sealed Attic", nbsp, nbsp, nbsp],
            [
                "<b>Total</b>",
                f"<b>{attrs['builder_electric_incentive']}</b>",
                f"<b>{attrs['builder_gas_incentive']}</b>",
                f"<b>{attrs['builder_sle_total']}</b>",
            ],
            [nbsp, nbsp, nbsp, nbsp],
            [
                "<b><u>Verifier Detailed Incentives</u></b>",
                "<b><u>ENH Electric</u></b>",
                "<b><u>ENH Gas</u></b>",
                "<b><u>SLE</u></b>",
            ],
            [
                "Verifier Performance Incentive",
                attrs["rater_electric_baseline"],
                attrs["rater_gas_baseline"],
                nbsp,
            ],
            ["Verifier DEI", nbsp, nbsp, nbsp],
            ["Verifier Solar Ready", nbsp, nbsp, attrs["solar_ready_verifier_incentive"]],
            [
                "<b>Total</b>",
                f"<b>{attrs['rater_electric_incentive']}</b>",
                f"<b>{attrs['rater_gas_incentive']}</b>",
                f"<b>{attrs['rater_sle_total']}</b>",
            ],
        ]

        if attrs["heat_type"] is not None:
            field = 1 if attrs["heat_type"] == HeatType.ELECTRIC else 2

            idx = data.index(next(x for x in data if x[0] == "Builder DEI"))
            data[idx][field] = attrs["cobid_builder_incentive"]

            idx = data.index(next(x for x in data if x[0] == "Fire Rebuild- Triple Pane Windows"))
            data[idx][field] = attrs["triple_pane_window_incentive"]
            idx = data.index(
                next(x for x in data if x[0] == "Fire Rebuild- Exterior Rigid Insulation")
            )
            data[idx][field] = attrs["rigid_insulation_incentive"]
            idx = data.index(next(x for x in data if x[0] == "Fire Rebuild- Sealed Attic"))
            data[idx][field] = attrs["sealed_attic_incentive"]

            idx = data.index(next(x for x in data if x[0] == "Verifier DEI"))
            data[idx][field] = attrs["cobid_verifier_incentive"]

        return data

    def get_incentive_table(self, **attrs: dict) -> list:
        return [
            ["Builder EPS Gas Incentive", attrs["builder_gas_incentive"]],
            ["Builder EPS Electric Incentive", attrs["builder_electric_incentive"]],
            ["Builder Solar Incentive", attrs["builder_sle_total"]],
            ["Total Builder Incentive", attrs["builder_incentive"]],
            ["Rater EPS Gas Incentive ", attrs["rater_gas_incentive"]],
            ["Rater EPS Electric Incentive", attrs["rater_electric_incentive"]],
            ["Rater Solar Incentive", attrs["rater_sle_total"]],
            ["Total Rater Incentive", attrs["rater_incentive"]],
            ["Savings (KWh)", attrs["savings_kwh"]],
            ["Savings (therms)", attrs["savings_therms"]],
            ["Percent Improvement (modeled vs. reference home)", attrs["percent_improvement"]],
            # ["Net Zero Solar Incentive", attrs["net_zero_solar_incentive"]],
            # ["ESH: EV Ready Incentive", attrs["ev_ready_builder_incentive"]],
            # ["ESH: Solar + Storage Incentive", attrs["solar_storage_builder_incentive"]],
            # ["Solar Ready Builder Incentive", attrs["solar_ready_builder_incentive"]],
            # ["Solar Ready Verifier Incentive", attrs["solar_ready_verifier_incentive"]],
            # ["DEI Builder Incentive", attrs["cobid_builder_incentive"]],
            # ["DEI Rater Incentive", attrs["cobid_verifier_incentive"]],
            # ["Triple Pane Window Incentive", attrs["triple_pane_window_incentive"]],
            # ["Rigid Insulation Incentive", attrs["rigid_insulation_incentive"]],
            # ["Sealed Attic Incentive", attrs["sealed_attic_incentive"]],
            # ["Heat Pump Water Heater Deduction", attrs["heat_pump_water_heater_incentive"]],
        ]

    def get_reportlab_table(self, styles: dict | None = None) -> Table:
        if styles is None:
            styles = getSampleStyleSheet()

        bold = styles["Bold"]
        normal = styles["Normal"]
        row_height = 0.2 * inch

        def fill(num: int) -> list:
            return [""] * num

        # This has two tables where one is 3x and the other is 2x. We create a 6x where we do a lot of spans.
        row = 0
        data = [
            [
                Paragraph(
                    "Program Incentives & Savings Summary", style=styles.get("centered-bold", bold)
                )
            ]
            + fill(5)
        ]
        row_heights = [row_height]
        style = [
            ("SPAN", (0, row), (5, row)),
        ]

        # Add a blank row
        row += 1
        data.append(fill(6))
        row_heights.append(row_height * 0.5)
        style.append(("SPAN", (0, row), (5, row)))

        attrs = self.to_representation(self.instance)
        for row, (key, value) in enumerate(self.get_incentive_table(**attrs), start=row + 1):
            data.append(
                [Paragraph(key, style=bold)] + fill(3) + [Paragraph(value, style=normal)] + fill(1)
            )
            row_heights.append(row_height)
            style.append(("SPAN", (0, row), (3, row)))
            style.append(("SPAN", (4, row), (5, row)))

        # Add the footnote
        note = (
            "<i>* Some homes may show a difference of up to $1 between amounts presented in the"
            "“Detailed Incentives” section and “Program Incentives & Saving Summary”. The detailed "
            "section displays whole dollar amounts without decimals, but the program includes the decimals "
            "when rounding-up to reach the full incentive amount in the summary.</i>"
        )
        row += 1
        p_style = ParagraphStyle(name="tiny", parent=normal, fontSize=8)
        data.append([Paragraph(note, style=p_style)] + fill(5))
        row_heights.append(row_height * 3)
        style.append(("SPAN", (0, row), (5, row)))

        # Add next header - blank followed by header followed by blank
        row += 1
        data.append(fill(6))
        row_heights.append(row_height * 0.5)
        style.append(("SPAN", (0, row), (5, row)))

        row += 1
        data.append(
            [Paragraph("Detailed Incentives", style=styles.get("centered-bold", bold))] + fill(5)
        )
        row_heights.append(row_height)
        style.append(("SPAN", (0, row), (5, row)))

        row += 1
        data.append(fill(6))
        row_heights.append(row_height * 0.5)
        style.append(("SPAN", (0, row), (5, row)))

        # Now add in the new details.
        for row, (key, ele, gas, sle) in enumerate(self.get_detail_table(**attrs), start=row + 1):
            data.append(
                [Paragraph(key, style=bold)]
                + fill(2)
                + [
                    Paragraph(ele, style=normal),
                    Paragraph(gas, style=normal),
                    Paragraph(sle, style=normal),
                ]
            )
            style.append(("SPAN", (0, row), (2, row)))
            row_heights.append(row_height)

        assert len(data) == len(row_heights), "Mismatch"
        return Table(data, style=style, rowHeights=row_heights)
