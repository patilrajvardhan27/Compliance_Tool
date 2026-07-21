"""Performance Compliance Report screen -- Python rendering of lib1/ReportPerformance.jrxml
(the report shown in image.png): Building Information, Construction Information, Performance
Analysis, Annual Thermal Load, Annual Site/Source Energy, CO2, and the Class 1-8 bar chart.
"""
from __future__ import annotations

from PySide6.QtCharts import QBarCategoryAxis, QBarSeries, QBarSet, QChart, QChartView, QValueAxis
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import (
    QDialog, QDialogButtonBox, QGridLayout, QGroupBox, QLabel, QScrollArea, QVBoxLayout, QWidget,
)

from tunbeec.calc.performance_report import PerformanceReport


def _row(grid: QGridLayout, row: int, label: str, value) -> None:
    grid.addWidget(QLabel(f"<b>{label}</b>"), row, 0)
    grid.addWidget(QLabel(str(value)), row, 1)


class PerformanceReportDialog(QDialog):
    def __init__(self, report: PerformanceReport, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Performance Compliance Report")
        self.resize(760, 820)

        outer = QVBoxLayout(self)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        v = QVBoxLayout(content)

        title = QLabel("Performance Compliance Report")
        title.setStyleSheet("font-size: 18px; font-weight: bold; background:#2b3a8f; color:white; padding:8px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.addWidget(title)

        gb_bldg = QGroupBox("Building Information")
        g1 = QGridLayout(gb_bldg)
        _row(g1, 0, "NAME:", report.bldg_name)
        _row(g1, 1, "LOCATION:", report.bldg_loc)
        _row(g1, 2, "TYPE:", report.bldg_type)
        _row(g1, 3, "SECTOR:", report.bldg_sector)
        _row(g1, 4, "ADDRESS:", report.bldg_address)
        _row(g1, 5, "CATEGORY:", report.bldg_category)
        if report.bldg_star:
            _row(g1, 6, "HOTEL GRADE:", report.bldg_star)
        v.addWidget(gb_bldg)

        gb_const = QGroupBox("Construction Information")
        g2 = QGridLayout(gb_const)
        _row(g2, 0, "Wall U-Value [W/m2.K]:", f"{report.ext_wall_const_u:.2f}")
        _row(g2, 1, "  South U:", f"{report.ext_wall_const_south_u:.2f}")
        _row(g2, 2, "  North U:", f"{report.ext_wall_const_north_u:.2f}")
        _row(g2, 3, "  East U:", f"{report.ext_wall_const_east_u:.2f}")
        _row(g2, 4, "  West U:", f"{report.ext_wall_const_west_u:.2f}")
        _row(g2, 5, "Roof U-Value [W/m2.K]:", f"{report.roof_const_u:.2f}")
        row = 6
        for idx in sorted(report.glass_u):
            _row(g2, row, f"Glass {idx} U / SC:", f"{report.glass_u[idx]:.2f} / {report.glass_sc.get(idx, 0):.2f}")
            row += 1
        v.addWidget(gb_const)

        gb_perf = QGroupBox("Performance Analysis")
        g3 = QGridLayout(gb_perf)
        g3.addWidget(QLabel("<b></b>"), 0, 0)
        g3.addWidget(QLabel("<b>Compliance</b>"), 0, 1)
        g3.addWidget(QLabel("<b>Building</b>"), 0, 2)
        g3.addWidget(QLabel("Thermal loads (BECth) [kWh/m2.year]"), 1, 0)
        g3.addWidget(QLabel(f"{report.min_bec_th:.1f}"), 1, 1)
        g3.addWidget(QLabel(f"{report.bldg_bec_th:.1f}"), 1, 2)
        g3.addWidget(QLabel("CLASS"), 2, 0)
        g3.addWidget(QLabel(report.min_class), 2, 1)
        g3.addWidget(QLabel(report.bldg_class), 2, 2)
        verdict = QLabel(report.result)
        verdict.setStyleSheet(
            "font-weight: bold; color: " + ("green" if report.result == "Compliant" else "red") + ";"
        )
        g3.addWidget(QLabel("<b>Performance Compliance Result</b>"), 3, 0)
        g3.addWidget(verdict, 3, 2)
        v.addWidget(gb_perf)

        gb_load = QGroupBox("Annual Thermal Load [kWh/m2.year]")
        g4 = QGridLayout(gb_load)
        _row(g4, 0, "Heating:", f"{report.h_load:.1f}")
        _row(g4, 1, "Cooling:", f"{report.c_load:.1f}")
        _row(g4, 2, "Annual:", f"{report.a_load:.1f}")
        v.addWidget(gb_load)

        gb_energy = QGroupBox("Annual Site Energy [kWh/m2.year]")
        g5 = QGridLayout(gb_energy)
        _row(g5, 0, "Electricity:", f"{report.c_energy:.1f}")
        _row(g5, 1, "Gas:", f"{report.h_energy:.1f}")
        _row(g5, 2, "Annual:", f"{report.a_energy:.1f}")
        v.addWidget(gb_energy)

        gb_src = QGroupBox("Annual Source Energy / CO2 Emission")
        g6 = QGridLayout(gb_src)
        _row(g6, 0, "Source Energy [kWh/m2.year]:", f"{report.a_src_energy:.1f}")
        _row(g6, 1, "CO2 Emission [kg/m2.year]:", f"{report.a_co2:.1f}")
        v.addWidget(gb_src)

        v.addWidget(self._build_chart(report))

        scroll.setWidget(content)
        outer.addWidget(scroll)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(self.accept)
        outer.addWidget(buttons)

    @staticmethod
    def _build_chart(report: PerformanceReport) -> QChartView:
        compliance_set = QBarSet("Compliance")
        building_set = QBarSet("Building")
        compliance_set.setColor(QColor("#d9534f"))
        building_set.setColor(QColor("#337ab7"))
        categories = []
        for row in report.class_rows:
            categories.append(row.class_name)
            compliance_set.append(row.class_value)
            building_set.append(float(row.class_bldg) if row.class_bldg else 0.0)

        series = QBarSeries()
        series.append(compliance_set)
        series.append(building_set)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("[kWh/m2.year]")
        axis_y = QBarCategoryAxis()
        axis_y.append(categories)
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_y)
        axis_x = QValueAxis()
        max_val = max([row.class_value for row in report.class_rows] + [report.bldg_bec_th]) * 1.1
        axis_x.setRange(0, max_val)
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axis_x)
        chart.legend().setVisible(True)

        view = QChartView(chart)
        view.setRenderHint(QPainter.RenderHint.Antialiasing)
        view.setMinimumHeight(280)
        return view
