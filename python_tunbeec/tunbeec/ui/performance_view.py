"""Performance Compliance Report screen -- Python rendering of lib1/ReportPerformance.jrxml
(the report shown in image.png): ANME masthead, blue section banners, Building/Construction
Information, Performance Analysis, Annual Thermal Load, Annual Site/Source Energy, CO2, and
the Class 1-8 horizontal bar chart with the building's value overlaid on its matched class.
"""
from __future__ import annotations

from PySide6.QtCharts import (
    QAbstractBarSeries, QBarCategoryAxis, QBarSet, QChart, QChartView, QHorizontalBarSeries,
    QValueAxis,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QPainter
from PySide6.QtWidgets import (
    QDialog, QDialogButtonBox, QGridLayout, QLabel, QScrollArea, QVBoxLayout, QWidget,
)

from tunbeec.calc.performance_report import PerformanceReport
from tunbeec.ui.report_style import COMPLIANT_GREEN, NON_COMPLIANT_RED, banner, title_header

# Series colors from the original ReportPerformance.jrxml chart (image.png).
_COMPLIANCE_RED = "#e8635c"
_BUILDING_BLUE = "#3f51d8"


def _grid(rows_data: list[tuple[str, str]], columns: int = 2) -> QWidget:
    """Lay out (label, value) pairs in `columns` label/value column pairs, like the jrxml."""
    w = QWidget()
    g = QGridLayout(w)
    g.setHorizontalSpacing(18)
    per_col = (len(rows_data) + columns - 1) // columns
    for i, (label, value) in enumerate(rows_data):
        col_group, row = divmod(i, per_col)
        lbl = QLabel(label)
        lbl.setStyleSheet("font-weight: bold; font-size: 10.5pt;")
        val = QLabel(value)
        val.setStyleSheet("font-size: 10.5pt;")
        g.addWidget(lbl, row, col_group * 2)
        g.addWidget(val, row, col_group * 2 + 1)
    for c in range(columns):
        g.setColumnStretch(c * 2 + 1, 1)
    return w


class PerformanceReportDialog(QDialog):
    def __init__(self, report: PerformanceReport, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Performance Compliance Report")
        self.resize(860, 900)

        outer = QVBoxLayout(self)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        content.setStyleSheet("background: white;")
        v = QVBoxLayout(content)
        v.setSpacing(10)

        v.addWidget(title_header("Performance Compliance Report"))

        v.addWidget(banner("Building Information"))
        bldg_rows = [
            ("NAME:", report.bldg_name), ("LOCATION:", report.bldg_loc),
            ("TYPE:", report.bldg_type), ("SECTOR:", report.bldg_sector),
            ("CATEGORY:", report.bldg_category), ("HOTEL GRADE:", report.bldg_star or "-"),
            ("ADDRESS:", report.bldg_address),
        ]
        v.addWidget(_grid(bldg_rows, columns=2))

        v.addWidget(banner("Construction Information"))
        const_rows = [
            ("Wall U-Value:", f"{report.ext_wall_const_u:.2f}  [W/m2.K]"),
            ("South U:", f"{report.ext_wall_const_south_u:.2f}  [W/m2.K]"),
            ("North U:", f"{report.ext_wall_const_north_u:.2f}  [W/m2.K]"),
            ("East U:", f"{report.ext_wall_const_east_u:.2f}  [W/m2.K]"),
            ("West U:", f"{report.ext_wall_const_west_u:.2f}  [W/m2.K]"),
            ("Roof U-Value:", f"{report.roof_const_u:.2f}  [W/m2.K]"),
        ]
        glass_rows = [
            (f"Glass {idx} U / SC:", f"{report.glass_u[idx]:.2f} [W/m2.K]  /  {report.glass_sc.get(idx, 0):.2f}")
            for idx in sorted(report.glass_u)
        ]
        v.addWidget(_grid(const_rows + glass_rows, columns=2))

        v.addWidget(banner("Performance Analysis"))
        perf = QWidget()
        g3 = QGridLayout(perf)
        hdr_font = "font-weight: bold; font-size: 10.5pt;"
        g3.addWidget(QLabel(""), 0, 0)
        for col, name in ((1, "Compliance"), (2, "Building")):
            lbl = QLabel(name)
            lbl.setStyleSheet(hdr_font)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            g3.addWidget(lbl, 0, col)
        lbl_bec = QLabel("Thermal loads (BECth) for conditioned space [kWh/m2.year]")
        lbl_bec.setStyleSheet("font-size: 10.5pt;")
        g3.addWidget(lbl_bec, 1, 0)
        for col, value in ((1, f"{report.min_bec_th:.1f}"), (2, f"{report.bldg_bec_th:.1f}")):
            lbl = QLabel(value)
            lbl.setStyleSheet("font-size: 10.5pt;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            g3.addWidget(lbl, 1, col)
        lbl_class = QLabel("CLASS")
        lbl_class.setStyleSheet(hdr_font)
        g3.addWidget(lbl_class, 2, 0)
        for col, value in ((1, report.min_class), (2, report.bldg_class)):
            lbl = QLabel(value)
            lbl.setStyleSheet("font-size: 10.5pt;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            g3.addWidget(lbl, 2, col)
        lbl_res = QLabel("Performance Compliance Result")
        lbl_res.setStyleSheet(f"font-weight: bold; font-size: 11pt; color: {NON_COMPLIANT_RED};")
        g3.addWidget(lbl_res, 3, 0)
        verdict = QLabel(report.result)
        verdict.setAlignment(Qt.AlignmentFlag.AlignCenter)
        verdict.setStyleSheet(
            "font-weight: bold; font-size: 11pt; color: "
            + (COMPLIANT_GREEN if report.result == "Compliant" else NON_COMPLIANT_RED) + ";"
        )
        g3.addWidget(verdict, 3, 2)
        g3.setColumnStretch(0, 2)
        g3.setColumnStretch(1, 1)
        g3.setColumnStretch(2, 1)
        v.addWidget(perf)

        v.addWidget(banner("Annual Loads / Energy / Emissions"))
        energy_rows = [
            ("Annual Thermal Load", "[kWh/m2.year]"),
            ("Heating:", f"{report.h_load:.1f}"),
            ("Cooling:", f"{report.c_load:.1f}"),
            ("Annual:", f"{report.a_load:.1f}"),
            ("Annual Site Energy", "[kWh/m2.year]"),
            ("Electricity:", f"{report.c_energy:.1f}"),
            ("Gas:", f"{report.h_energy:.1f}"),
            ("Annual:", f"{report.a_energy:.1f}"),
            ("Annual Source Energy", "[kWh/m2.year]"),
            ("", f"{report.a_src_energy:.1f}"),
            ("Annual CO2 Emission", "[kg/m2.year]"),
            ("", f"{report.a_co2:.1f}"),
        ]
        v.addWidget(_grid(energy_rows, columns=2))

        v.addWidget(self._build_chart(report))

        scroll.setWidget(content)
        outer.addWidget(scroll)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(self.accept)
        outer.addWidget(buttons)

    @staticmethod
    def _build_chart(report: PerformanceReport) -> QChartView:
        """Class 1-8 horizontal bar chart, mirroring the jrxml chart: red bars for the class
        thresholds ("Compliance") and a blue bar for the building's own BECth, drawn on the
        row of the class the building landed in. Class 1 renders at the top."""
        compliance_set = QBarSet("Compliance")
        building_set = QBarSet("Building")
        compliance_set.setColor(QColor(_COMPLIANCE_RED))
        building_set.setColor(QColor(_BUILDING_BLUE))
        compliance_set.setLabelColor(QColor("#333333"))
        building_set.setLabelColor(QColor("#333333"))

        categories = []
        # QBarCategoryAxis on a horizontal series lays categories bottom-to-top, so feed the
        # rows reversed to keep Class 1 at the top like the original report.
        for row in reversed(report.class_rows):
            categories.append(row.class_name)
            compliance_set.append(row.class_value)
            building_set.append(float(row.class_bldg) if row.class_bldg else 0.0)

        series = QHorizontalBarSeries()
        series.append(compliance_set)
        series.append(building_set)
        series.setLabelsVisible(True)
        series.setLabelsPosition(QAbstractBarSeries.LabelsPosition.LabelsOutsideEnd)
        series.setLabelsFormat("@value")
        series.setLabelsPrecision(4)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("[kWh/m2.year]")
        title_font = QFont()
        title_font.setBold(True)
        chart.setTitleFont(title_font)

        axis_y = QBarCategoryAxis()
        axis_y.append(categories)
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_y)

        axis_x = QValueAxis()
        max_val = max([row.class_value for row in report.class_rows] + [report.bldg_bec_th])
        axis_x.setRange(0, max_val * 1.15)
        axis_x.setLabelFormat("%.0f")
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axis_x)

        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)

        view = QChartView(chart)
        view.setRenderHint(QPainter.RenderHint.Antialiasing)
        view.setMinimumHeight(360)
        return view
