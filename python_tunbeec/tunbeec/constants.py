# Unit-conversion and code-compliance constants.
# Ported verbatim from the decompiled Java (method/SimData.java, method/PerformanceOld.java).
# These are regulatory/simulation constants -- do not "clean up" the values.

# SI -> IP (DOE-2 uses IP internally)
M_TO_FT = 3.28084
FT_TO_M = 0.3048
M2_TO_FT2 = 10.76391
FT2_TO_M2 = 0.09290304
MBTU_TO_KWH = 293.0711  # 1 MBtu (million Btu) -> kWh

# Envelope/material SI -> IP factors used when emitting DOE-2 MATERIAL/CONSTRUCTION/GLASS-TYPE blocks
HEAT_RATE_SI_TO_IP = 5.678269       # U-VALUE: W/m2.K -> Btu/hr.ft2.F
CONDUCTIVITY_SI_TO_IP = 0.5777893   # CONDUCTIVITY / GLASS-CONDUCT
DENSITY_SI_TO_IP = 0.06242797       # MATERIAL DENSITY
SPEC_HEAT_SI_TO_IP = 2.388459e-4    # MATERIAL SPECIFIC-HEAT

FRAME_CONDUCT = 3.079  # fixed literal window frame conductance (BldgWindow.java)

# CO2 emission factors (method/PerformanceOld.calcBldgEnergy)
# annCO2 = electricity_kWh * 3.0 * 0.69 + gas_kWh * 0.170607064
CO2_ELEC_SOURCE_MULTIPLIER = 3.0
CO2_ELEC_FACTOR = 0.69          # kgCO2/kWh-source
CO2_GAS_FACTOR = 0.170607064    # kgCO2/kWh gas (direct combustion)

# Villa BDL template hardcoded reference geometry (method/SimData.java static block)
VILLA_TEMPLATE_ONE_FLOOR_AREA_FT2 = 794.6
SOUTH_WALL_WIDTH_VILLA = 34.7
NORTH_WALL_WIDTH_VILLA = 34.7
EAST_WALL_WIDTH_VILLA = 32.9
WEST_WALL_WIDTH_VILLA = 32.9
SOUTH_WALL_RATIO_1_VILLA = 0.36023054755043227
SOUTH_WALL_RATIO_2_VILLA = 0.23631123919308353
SOUTH_WALL_RATIO_3_VILLA = 0.4034582132564841
NORTH_WALL_RATIO_1_VILLA = 0.36023054755043227
NORTH_WALL_RATIO_2_VILLA = 0.23631123919308353
NORTH_WALL_RATIO_3_VILLA = 0.4034582132564841
EAST_WALL_RATIO_1_VILLA = 0.19452887537993924
EAST_WALL_RATIO_2_VILLA = 0.425531914893617
EAST_WALL_RATIO_3_VILLA = 0.3799392097264438
WEST_WALL_RATIO_1_VILLA = 0.3951367781155015
WEST_WALL_RATIO_2_VILLA = 0.303951367781155
WEST_WALL_RATIO_3_VILLA = 0.10638297872340426
WEST_WALL_RATIO_4_VILLA = 0.19452887537993924

# Class thresholds (kWh/m2.year), method/PerformanceOld.writeResult() -- hardcoded String[][] constants,
# NOT stored in the SQLite reference DB. Index 0 = Class 1 ... index 7 = Class 8.
CLASS_THRESHOLDS_RESIDENTIAL = [36, 41, 46, 51, 60, 72, 87, 300]
CLASS_THRESHOLDS_OFFICE = [75, 85, 95, 105, 125, 150, 180, 500]
CLASS_THRESHOLDS_HOTEL = [90, 100, 110, 120, 135, 160, 190, 500]
CLASS_THRESHOLDS_HOSPITAL = [135, 145, 155, 165, 180, 200, 230, 500]

# Minimum-class-required tables (1-indexed class number below which the building fails compliance).
# "Non-compliant if achieved class index (1-based) >= this number."
MIN_CLASS_INDEX_RESIDENTIAL = 6  # must be Class 1-5 (<=60 kWh/m2.year) to pass
MIN_CLASS_INDEX_OFFICE_PUBLIC = 4
MIN_CLASS_INDEX_OFFICE_PRIVATE = 6
MIN_CLASS_INDEX_HOTEL_3STAR = 4
MIN_CLASS_INDEX_HOTEL_4STAR = 5
MIN_CLASS_INDEX_HOTEL_5STAR = 4
MIN_CLASS_INDEX_HOSPITAL_PUBLIC = 4
MIN_CLASS_INDEX_HOSPITAL_PRIVATE = 6

# Prescriptive-path climate-zone location table (method/Prescriptive.java)
CLIMATE_LOCATIONS = [
    ["TUNIS", "BIZERTE", "ARIANA", "NABEUL", "MAHDIA", "SOUSSE", "SFAX", "MEDENINE"],
    ["BEJA", "JENDOUBA", "KAIROUAN", "GAFSA", "SILIANA", "SIDI BOUZID"],
    ["KEBILI", "TOZEUR", "TATAOUINE", "MATMATA"],
]

# Prescriptive code tables: [climate][X1/X2 bracket] -> [wallU, roofU, glassU, glassSC]
CODE_RESIDENTIAL = [
    [[0.75, 1.1, 6.2, 0.95], [0.75, 1.1, 6.2, 0.7], [0.75, 1.1, 3.2, 0.85], [0.75, 1.1, 3.2, 0.75], [0.65, 0.8, 3.2, 0.7]],
    [[0.75, 1.1, 3.2, 0.95], [0.75, 0.8, 6.2, 0.95], [0.75, 1.1, 3.2, 0.7], [0.75, 0.7, 3.2, 0.7], [0.65, 0.7, 1.9, 0.6]],
    [[0.75, 1.1, 3.2, 0.85], [0.75, 0.8, 6.2, 0.8], [0.75, 1.1, 3.2, 0.6], [0.65, 0.7, 3.2, 0.7]],
]
CODE_COMM_PRIVATE = [
    [[0.75, 1.2, 6.2, 0.95], [0.75, 1.1, 6.2, 0.7], [0.75, 1.1, 6.2, 0.6], [0.75, 0.8, 6.2, 0.7], [0.75, 1.1, 3.2, 0.6]],
    [[0.75, 1.1, 6.2, 0.95], [0.75, 1.1, 6.2, 0.7], [0.75, 1.1, 1.9, 0.5], [0.75, 0.8, 3.2, 0.6], [0.65, 0.8, 1.9, 0.5]],
    [[0.75, 1.1, 6.2, 0.95], [0.75, 1.1, 6.2, 0.7], [0.75, 1.1, 1.9, 0.5], [0.55, 0.8, 3.2, 0.6], [0.75, 0.6, 1.9, 0.5], [0.55, 0.8, 1.9, 0.5]],
]
CODE_COMM_PUBLIC = [
    [[0.75, 1.2, 6.2, 0.95], [0.75, 1.1, 3.2, 0.6], [0.75, 1.1, 1.9, 0.5]],
    [[0.55, 0.6, 3.2, 0.8], [0.55, 1.1, 1.9, 0.5]],
    [[0.55, 1.1, 3.2, 0.6], [0.55, 0.8, 1.9, 0.5]],
]
