        WATER_HEATING_TYPE.put("None", RemWaterHeatingType.NONE);
        WATER_HEATING_TYPE.put("Conventional", RemWaterHeatingType.CONVENTIONAL);
        WATER_HEATING_TYPE.put("Instant water heater", RemWaterHeatingType.INSTANT);
        WATER_HEATING_TYPE.put("Heat pump", RemWaterHeatingType.HEAT_PUMP);
        WATER_HEATING_TYPE.put("Ground source heat pump", RemWaterHeatingType.GROUND_SOURCE_HEAT_PUMP);
        WATER_HEATING_TYPE.put("Integrated", RemWaterHeatingType.INTEGRATED);

        GSHP_PUMP_ENERGY_TYPE.put("Watts", RemGshpPumpEnergyType.WATTS);
        GSHP_PUMP_ENERGY_TYPE.put("kWh/yr", RemGshpPumpEnergyType.KWH_YR);

        //For REM conditioning equipment
        EQUIPMENT_LIBRARY_TYPE.put("Space Heating", RemEquipmentLibraryType.SPACE_HEATING);
        EQUIPMENT_LIBRARY_TYPE.put("Space Cooling", RemEquipmentLibraryType.SPACE_COOLING);
        EQUIPMENT_LIBRARY_TYPE.put("Water Heating", RemEquipmentLibraryType.WATER_HEATING);
        EQUIPMENT_LIBRARY_TYPE.put("Air-Source Heat Pump", RemEquipmentLibraryType.AIR_SOURCE_HEAT_PUMP);
        EQUIPMENT_LIBRARY_TYPE.put("Ground Source Heat Pump", RemEquipmentLibraryType.GROUND_SOURCE_HEAT_PUMP);
      //Note the typo in REM, probably an earlier version
        EQUIPMENT_LIBRARY_TYPE.put("Duel-Fuel Heat Pump", RemEquipmentLibraryType.DUAL_FUEL_HEAT_PUMP);
        EQUIPMENT_LIBRARY_TYPE.put("Dual Fuel Heat Pump", RemEquipmentLibraryType.DUAL_FUEL_HEAT_PUMP);
        //Integrated space/water heating doesn't seem to export, not sure what the key is.

        SYSTEM_TYPE.put("Fuel-fired air distribution", RemSystemType.FUEL_FIRED_AIR_DISTRIBUTION);
        SYSTEM_TYPE.put("Fuel-fired hydronic distribution", RemSystemType.FUEL_FIRED_HYDRONIC_DISTRIBUTION);
        SYSTEM_TYPE.put("Fuel-fired unit heater", RemSystemType.FUEL_FIRED_UNIT_HEATER);
        SYSTEM_TYPE.put("Fuel-fired unvented unit heater", RemSystemType.FUEL_FIRED_UNVENTED_UNIT_HEATER);
        SYSTEM_TYPE.put("Electric baseboard or radiant", RemSystemType.ELECTRIC_BASEBOARD_OR_RADIANT);
        SYSTEM_TYPE.put("Electric air distribution", RemSystemType.ELECTRIC_AIR_DISTRIBUTION);
        SYSTEM_TYPE.put("Electric hydronic distribution", RemSystemType.ELECTRIC_HYDRONIC_DISTRIBUTION);
        SYSTEM_TYPE.put("Air-source heat pump", RemSystemType.AIR_SOURCE_HEAT_PUMP);
        SYSTEM_TYPE.put("Ground-source heat pump", RemSystemType.GROUND_SOURCE_HEAT_PUMP);
        SYSTEM_TYPE.put("Air conditioner", RemSystemType.AIR_CONDITIONER);
        SYSTEM_TYPE.put("Evaporative cooler", RemSystemType.EVAPORATIVE_COOLER);
        SYSTEM_TYPE.put("None", RemSystemType.NONE);

        SYSTEM_EKOTROPE_TYPE.put(RemSystemType.FUEL_FIRED_AIR_DISTRIBUTION, EquipmentType.FURNACE);
        SYSTEM_EKOTROPE_TYPE.put(RemSystemType.FUEL_FIRED_HYDRONIC_DISTRIBUTION, EquipmentType.BOILER);
        SYSTEM_EKOTROPE_TYPE.put(RemSystemType.FUEL_FIRED_UNIT_HEATER, EquipmentType.CUSTOM);
        SYSTEM_EKOTROPE_TYPE.put(RemSystemType.FUEL_FIRED_UNVENTED_UNIT_HEATER, EquipmentType.CUSTOM);
        SYSTEM_EKOTROPE_TYPE.put(RemSystemType.ELECTRIC_BASEBOARD_OR_RADIANT, EquipmentType.RESISTANCE_HEATER);
        SYSTEM_EKOTROPE_TYPE.put(RemSystemType.ELECTRIC_AIR_DISTRIBUTION, EquipmentType.FURNACE);
        SYSTEM_EKOTROPE_TYPE.put(RemSystemType.ELECTRIC_HYDRONIC_DISTRIBUTION, EquipmentType.BOILER);
        SYSTEM_EKOTROPE_TYPE.put(RemSystemType.AIR_SOURCE_HEAT_PUMP, EquipmentType.AIR_SOURCE_HEAT_PUMP);
        SYSTEM_EKOTROPE_TYPE.put(RemSystemType.GROUND_SOURCE_HEAT_PUMP, EquipmentType.GROUND_SOURCE_HEAT_PUMP);
        SYSTEM_EKOTROPE_TYPE.put(RemSystemType.AIR_CONDITIONER, EquipmentType.AIR_CONDITIONER);
        SYSTEM_EKOTROPE_TYPE.put(RemSystemType.NONE, EquipmentType.CUSTOM);

        EFFICIENCY_TYPE.put("AFUE", EfficiencyType.AFUE);
        EFFICIENCY_TYPE.put("SEER", EfficiencyType.SEER);
        EFFICIENCY_TYPE.put("EER", EfficiencyType.EER);
        EFFICIENCY_TYPE.put("HSPF", EfficiencyType.HSPF);
        EFFICIENCY_TYPE.put("COP", EfficiencyType.COP);
        EFFICIENCY_TYPE.put("% EFF", EfficiencyType.EFFICIENCY);

        DUCT_LOCATION.put("Conditioned space", DuctLocation.CONDITIONED_SPACE);
        DUCT_LOCATION.put("Attic, exposed", DuctLocation.ATTIC_WELL_VENTED);
        DUCT_LOCATION.put("Open crawl/raised floor", DuctLocation.CRAWLSPACE_VENTED_INSULATED_FLOOR_ONLY);
        DUCT_LOCATION.put("Enclosed crawl space", DuctLocation.CRAWLSPACE_UNVENTED_INSULATED_FLOOR_ONLY);
        DUCT_LOCATION.put("Conditioned crawl space", DuctLocation.CONDITIONED_SPACE);
        DUCT_LOCATION.put("Unconditioned basement", DuctLocation.BASEMENT_UNINSULATED);
        DUCT_LOCATION.put("Conditioned basement", DuctLocation.CONDITIONED_SPACE);
        DUCT_LOCATION.put("Attic, under insulation", DuctLocation.ATTIC_WELL_VENTED);
        DUCT_LOCATION.put("Garage", DuctLocation.GARAGE);
        DUCT_LOCATION.put("Floor cavity over garage", DuctLocation.GARAGE);
        DUCT_LOCATION.put("Exterior wall", DuctLocation.EXTERIOR_WALLS);
        DUCT_LOCATION.put("Wall with no top plate", DuctLocation.EXTERIOR_WALLS);
        DUCT_LOCATION.put("Under slab floor", DuctLocation.UNDERSLAB);
        DUCT_LOCATION.put("Mobile home belly", DuctLocation.CRAWLSPACE_VENTED_UNINSULATED);
        DUCT_LOCATION.put("None", DuctLocation.CONDITIONED_SPACE);

        SHELL_LOCATION.put("Between conditioned space and ambient", EXPOSED_EXTERIOR);
        SHELL_LOCATION.put("Between conditioned space and ambient conditions", EXPOSED_EXTERIOR);
        SHELL_LOCATION.put("Between conditioned space and garage", UNCONDITIONED_ABOVE_GROUND_ROOM);
        SHELL_LOCATION.put("Between conditioned space and open crawl", VENTED_CRAWL);
        SHELL_LOCATION.put("Between conditioned space and attic", VENTED_ATTIC);
        SHELL_LOCATION.put("Between conditioned space and uncond bsmnt", UNCONDITIONED_BASEMENT);
        SHELL_LOCATION.put("Between conditioned space and enclosed crawl", UNVENTED_CRAWL);
        SHELL_LOCATION.put("Between conditioned space and enclosed crawl space", UNVENTED_CRAWL);
        SHELL_LOCATION.put("Between conditioned crawl and ambient", EXPOSED_EXTERIOR);
        SHELL_LOCATION.put("Between conditioned crawl and garage", UNCONDITIONED_ABOVE_GROUND_ROOM);
        SHELL_LOCATION.put("Between conditioned crawl and open crawl", VENTED_CRAWL);
        SHELL_LOCATION.put("Between conditioned crawl and ", EXPOSED_EXTERIOR);

        //TODO: UNCONDITIONED_BOUNDARY_WARNING
        //Set these to adiabatic because they shouldn't change our energy algorithm.
        SHELL_LOCATION.put("None", CONDITIONED_SPACE);
        SHELL_LOCATION.put("Between unconditioned bsmnt and ambient", CONDITIONED_SPACE);
        SHELL_LOCATION.put("Between unconditioned bsmnt and garage", CONDITIONED_SPACE);
        SHELL_LOCATION.put("Between unconditioned bsmnt and open crawl", CONDITIONED_SPACE);
        SHELL_LOCATION.put("Between enclosed crawl and ambient", CONDITIONED_SPACE);
        SHELL_LOCATION.put("Between enclosed crawl and garage", CONDITIONED_SPACE);
        SHELL_LOCATION.put("Between enclosed crawl and open crawl", CONDITIONED_SPACE);

        SHELL_LOCATION.put("Between cond and another cond unit (adiabatic)", CONDITIONED_SPACE);
        SHELL_LOCATION.put("Between conditioned space and another (adiabatic)", CONDITIONED_SPACE);

        SHELL_LOCATION.put("Between sealed attic and ambient", EXPOSED_EXTERIOR);

        CEILING_TYPE_TO_SHELL_LOCATION.put("Attic", VENTED_ATTIC);
        CEILING_TYPE_TO_SHELL_LOCATION.put("Vaulted", VAULTED_ROOF);
        CEILING_TYPE_TO_SHELL_LOCATION.put("Sealed Attic", SEALED_ATTIC);
        CEILING_TYPE_TO_SHELL_LOCATION.put("Adiabatic", CONDITIONED_SPACE);

        // Values taken from Remrate path layer interface
        FLOOR_COVERING_R.put(null, 0D);
        FLOOR_COVERING_R.put("Carpet", REMRATE_CARPET_R);
        FLOOR_COVERING_R.put("Tile", 0.05);
        FLOOR_COVERING_R.put("Hardwood", 0.68);
        FLOOR_COVERING_R.put("Vinyl", 0.05);
        FLOOR_COVERING_R.put("None", 0D);

        FLOOR_COVERING_MATERIAL.put(null, MaterialDefault.CUSTOM);
        FLOOR_COVERING_MATERIAL.put("Carpet", MaterialDefault.CARPET);
        FLOOR_COVERING_MATERIAL.put("Tile", MaterialDefault.CUSTOM);
        FLOOR_COVERING_MATERIAL.put("Hardwood", MaterialDefault.FINISH_WOOD);
        FLOOR_COVERING_MATERIAL.put("Vinyl", MaterialDefault.CUSTOM);
        FLOOR_COVERING_MATERIAL.put("None", MaterialDefault.CUSTOM);

        ORIENTATION.put("North", NORTH);
        ORIENTATION.put("South", SOUTH);
        ORIENTATION.put("East", EAST);
        ORIENTATION.put("West", WEST);

        ORIENTATION.put("Southeast", EAST);
        ORIENTATION.put("Southwest", WEST);
        ORIENTATION.put("Northeast", NORTH);
        ORIENTATION.put("Northwest", NORTH);

        INFILTRATION_UNIT.put("Natural ACH", ACH_NATURAL);
        INFILTRATION_UNIT.put("ACH @ 50 Pascals", ACH_50);
        INFILTRATION_UNIT.put("CFM @ 50 Pascals", CFM_50);
        INFILTRATION_UNIT.put("CFM @ 25 Pascals", null);
//        INFILTRATION_UNIT.put("Eff. Leakage Area (in)", ELA);//Should be superscript "2" after "in".  UTF8 won't accept it.
        INFILTRATION_UNIT.put("Specific Leakage Area", SLA);
        INFILTRATION_UNIT.put("ELA/100 sf shell", null);

        INFILTRATION_MEASUREMENT.put("Blower door test", TESTED);
        INFILTRATION_MEASUREMENT.put("User estimate", UNTESTED);
        INFILTRATION_MEASUREMENT.put("Code default", UNTESTED);
        INFILTRATION_MEASUREMENT.put("Tracer gas test", UNTESTED);

        SHELTER_CLASS.put("1", I);
        SHELTER_CLASS.put("2", II);
        SHELTER_CLASS.put("3", III);
        SHELTER_CLASS.put("4", IV);
        SHELTER_CLASS.put("5", V);

        RESIDENCE_TYPE.put("Multi-family, whole building", MULTI_UNIT_APARTMENT);
        RESIDENCE_TYPE.put("Duplex, whole building", MULTI_UNIT_APARTMENT);
        RESIDENCE_TYPE.put("Single-family detached", SINGLE_FAMILY_HOUSE);
        RESIDENCE_TYPE.put("Townhouse, end unit", MULTI_UNIT_TOWN_HOUSE);
        RESIDENCE_TYPE.put("Townhouse, inside unit", MULTI_UNIT_TOWN_HOUSE);
        RESIDENCE_TYPE.put("Apartment, end unit", MULTI_UNIT_APARTMENT);
        RESIDENCE_TYPE.put("Apartment, inside unit", MULTI_UNIT_APARTMENT);
        RESIDENCE_TYPE.put("Duplex, single unit", MULTI_UNIT_APARTMENT);
        RESIDENCE_TYPE.put("Mobile Home", SINGLE_FAMILY_HOUSE);

        FUEL_TYPE.put("Natural gas", NATURAL_GAS);
        FUEL_TYPE.put("Propane", PROPANE);
        FUEL_TYPE.put("Fuel oil", OIL);
        FUEL_TYPE.put("Electric", ELECTRIC);
        FUEL_TYPE.put("Kerosene", OIL);
        FUEL_TYPE.put("Wood", WOOD);



        // These come from REM/Rate's Window help section
        ADJACENT_SHADING.put("None", 1D);
        ADJACENT_SHADING.put("Some", .7);
        ADJACENT_SHADING.put("Most", .4);
        ADJACENT_SHADING.put("Complete", .1);

        VENTILATION_TYPE.put("Balanced", VentilationType.HRV);
        VENTILATION_TYPE.put("Exhaust Only", VentilationType.EXHAUST_ONLY);
        VENTILATION_TYPE.put("Supply Only", VentilationType.SUPPLY_ONLY);
        VENTILATION_TYPE.put("Air Cycler", VentilationType.BALANCED);
    }
