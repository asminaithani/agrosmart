import asyncio
from typing import Dict, Any

async def calculate_sustainability(crop_data: Dict[str, Any], user_inputs: Dict[str, Any]) -> Dict[str, Any]:
    # Simulate slight delay to mimic DB lookup or complex computation
    await asyncio.sleep(0.01)
    
    field_size_hectares = float(user_inputs.get("field_size_hectares", 1.0))
    
    flood_baseline = 15000  # L/hectare/season
    drip_usage = 6000
    sprinkler_usage = 9000
    
    conventional_emission = 2.5  # kg CO₂/kg crop yield
    sustainable_emission = 1.4
    
    rainfall = float(user_inputs.get("rainfall", 0))
    crop_name = crop_data.get("top_recommendation", "rice").lower()
    
    if rainfall < 500 and crop_name in ["rice", "sugarcane"]:
        recommended_method_usage = drip_usage
    elif 500 <= rainfall <= 1000:
        recommended_method_usage = sprinkler_usage
    else:
        # Optimized flood irrigation
        recommended_method_usage = 12000
        
    water_saved_liters = (flood_baseline - recommended_method_usage) * field_size_hectares
    carbon_reduction_pct = ((conventional_emission - sustainable_emission) / conventional_emission) * 100
    
    # Energy estimate: pumping 1000L of water uses approx 0.5 kWh
    energy_saved_kwh = water_saved_liters * 0.0005
    
    water_saved_pct = ((flood_baseline - recommended_method_usage) / flood_baseline) * 100

    # Estimates: pumping energy (above) x grid emission factor, per hectare.
    # 0.82 kg CO2/kWh is an assumed grid average; 0.17 kg CO2/km is an assumed passenger car.
    GRID_KG_CO2_PER_KWH = 0.82
    CAR_KG_CO2_PER_KM = 0.17
    carbon_reduced_kg_ha = max(0.0, energy_saved_kwh / field_size_hectares) * GRID_KG_CO2_PER_KWH
    km_not_driven = carbon_reduced_kg_ha / CAR_KG_CO2_PER_KM

    return {
        "carbon_reduced_kg_ha": round(carbon_reduced_kg_ha, 2),
        "km_not_driven": int(round(km_not_driven)),
        "sustainable_development": True,
        "carbon_footprint_reduction_pct": round(carbon_reduction_pct, 2),
        "carbon_reduction_pct": round(carbon_reduction_pct, 2),
        "emission_kg_per_season": sustainable_emission,
        "water_saved_pct": round(max(0.0, water_saved_pct), 1),
        "water_saved_liters": max(0, water_saved_liters),
        "energy_saved_kwh": max(0, round(energy_saved_kwh, 2))
    }
