"""views.py: Django customer_earth_advantage"""


__author__ = "Michael Jeffrey"
__version__ = "77.0.11"
__version_info__ = (77, 0, 11)
__date__ = "8/9/17 2:53 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Michael Jeffrey",
]
__license__ = "See the file LICENSE.txt for licensing information."


FAKE_EAAA_DATA = {
    # Page 1
    "Property Address": "one",
    "Property Tax ID": "two",
    "Representative Type": "three",
    "Representative Name": "four",
    "Representative phoneemail": "five",
    "Performance Label": "six",
    "Performance Label Score": "seven",
    "Estimated Energy Costs": "eight",
    "Estimated Energy Costs Term": "nine",
    "Performance Label Date": "ten",
    "Benchmark": "eleven",
    "Benchmark Score": "twelve",
    "Certification": "thirteen",
    "Level": "fourteen",
    "Year": "fifteen",
    "open left 1": "sixteen",
    "open left 2": "seventeen",
    "open left 3": "eighteen",
    "open left 4": "nineteen",
    "open left 5": "twenty",
    "open left 6": "twenty one",
    "open left 7": "twenty two",
    "open left 8": "twenty three",
    "open left 9": "twenty four",
    "open left 10": "twenty five",
    "open left 11": "twenty six",
    "open left 12": "twenty seven",
    "open left 13": "twenty eight",
    "open left 14": "twenty nine",
    "open left 15": "thirty",
    "open left 16": "thirty one",
    # Page 2
    "Air Conditioning Efficiency": "thirty two",
    "Furnace Efficiency": "thirty three",
    "Heat Pump Efficiency": "thirty four",
    "Ductless Heat Pump System Efficiency": "thirty five",
    "Secondary Heat Pump Type": "thirty six",
    "Secondary Heat Pump Efficiency": "thirty seven",
    "Heating System": "thirty eight",
    "Tankless Water Heater Efficiency": "thirty nine",
    "Water Heater Efficiency": "forty",
    "Mechanical Ventilation Type": "forty one",
    # Page 3
    "System Size Capacity": "forty two",
    "PV Panel Manufacturer": "forty three",
    "Est Annual Production": "forty four",
    "PV Panel Age": "forty five",
    "Array location": "forty six",
    "PV Panel Warranty": "forty seven",
    "Array Ownership": "forty eight",
    "Inverter Manufacturer": "forty nine",
    "Interter Age": "fifty",
    "Inverter Warranty": "fifty one",
    "Solar Thermal Type": "fifty two",
    "Storage Tank Size": "fifty three",
    "Solar Thermal Manufacturer": "fifty four",
    "Solar Energy Factor SEF": "fifty five",
    "Solar Thermal Age": "fifty six",
    "Solar Thermal Warranty": "fifty seven",
    "Solar Thermal Backup System": "fifty eight",
    "Solar Thermal Backup System Fuel": "fifty nine",
    "open left 17": "sixty",
    "open left 18": "sixty one",
    "open left 19": "sixty two",
    "open left 20": "sixty three",
    "open left 21": "sixty four",
    "open left 22": "sixty five",
    "open left 23": "sixty six",
    "open left 24": "sixty seven",
    "open left 25": "sixty eight",
    "open left 26": "sixty nine",
    "open left 27": "seventy",
    "open left 28": "seventy one",
    "open left 29": "seventy two",
}
