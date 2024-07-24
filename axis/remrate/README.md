#Remrate *(remrate)*
----------------------------

## Description

This provides a number of utilities in dealing with REM/Rate®.  It has Windows Specific Tasks.


## Authors

* Steven Klass
* Rajesh Pappula
* Eric Walker
* Amit Kumar Pathak
* Tim Valenta
* Shawn Pike

# Current REM/Rate Validations

### How to read this.

The BLG Validation is done by comparing the same locations in two different sources.
To do this, we take all the different sources and turn it into the same shape. This allows us to have more than 2 sources when we're comparing things, and different results depending on which sources do not match.

The `Path` is where the data is being mapped to. If you would like to know specifically where the data is coming from for a source feel free to ask.

The name of the tables is which data source introduces these checks. In the case of Checklist Answers, there's no reason to look at the keys that match to the Checklist data if there is none.

`Default Status` is what will be returned if the sources provided do not match. This can be preceded by specific checks of combinations of sources.
`Simulation - Blg` is what will be returned if specifically the Simulation and Blg file disagree on values.
`Home Status - Blg` is what will be returned if specifically the Home Status and Blg file disagree on values.
`Checklist - Blg` is what will be returned if specifically the Checklist Answers and Blg file disagree on values.

The ones that say `complex` I tried to document at the bottom. If you have questions it might be easier to ask over a call.

---

Rem Data
---
Path | Default Status
--- | ---
version | warning
building.project_info.propertyaddress | warning
building.project_info.buildername | warning
building.project_info.buildingname | warning
building.project_info.ratingorgname | warning
building.project_info.ratername | warning
building.project_info.buildername | warning
building.building_info.condArea | error
building.building_info.bldgVolume | error
building.building_info.numBedrooms | error
building.building_info.housingType | error
building.building_info.foundationType | error

Project
---
Path | Default Status | Simulation - Blg | Home Status - Blg
--- | --- | --- | ---
building.project_info.buildername | warning | default | default
building.project_info.ratingorgname | warning | default | default
building.project_info.propertycity | warning | default | default
building.project_info.propertystate | warning | default | default
building.project_info.propertyzip | warning | default | default
building.project_info.developmentname | warning | default | default
building.project_info.modelname | info | default | warning
building.building_info.condArea | warning | error | default

Checklist Answers
---
Path | Default Status | Simulation - Blg | Checklist - Blg
--- | --- | --- | ---
building.building_info.volume | warning | error | default
building.building_info.numBedrooms | warning | error | default
calculations.dominant_window.u_value | info | error | warning
calculations.dominant_window.solar_heat_gain_coefficient | info | error | warning
calculations.dominant_skylight.u_value | warning | error | default
calculations.dominant_skylight.solar_heat_gain_coefficient | warning | error | default
building.lights_and_appliances.percentCFL | warning | error | default
building.lights_and_appliances.dishwasherEf | warning | error | default
building.lights_and_appliances.dishwasherkWhYear | warning | error | default
calculations.dominant_cooling.efficiency* | complex | complex | complex
calculations.dominant_heating.efficiency** | complex | complex | complex
calculations.dominant_heating.location | info | error | warning
calculations.dominant_hot_water.tank_size | info | error | warning
calculations.dominant_hot_water.energy_factor | info | error | warning
calculations.dominant_hot_water.location | info | error | warning
calculations.dominant_duct_system.total | info | default | warning


* *Dominant Cooling Efficiency: If there are units, and the BLG and Checklist are not matched returns as `warning`.
* **Dominant Heating Efficiency: Compares Dominant heating type declared by the BLG to correct Checklist question. If they do not match, returned as `warning`.

## Copyright

Copyright 2011-2023 Pivotal Energy Solutions.  All rights reserved.
