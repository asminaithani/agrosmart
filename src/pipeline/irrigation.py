import asyncio
from typing import Dict, Any

async def recommend_irrigation(crop_data: Dict[str, Any], user_inputs: Dict[str, Any]) -> Dict[str, Any]:
    await asyncio.sleep(0.01)
    
    rainfall = float(user_inputs.get("rainfall", 0))
    crop = crop_data.get("top_recommendation", "rice").lower()
    field_size_hectares = float(user_inputs.get("field_size_hectares", 1.0))
    
    drip_usage = 6000
    sprinkler_usage = 9000
    optimized_flood_usage = 12000
    
    if rainfall < 500 and crop in ["rice", "sugarcane"]:
        method = "Drip Irrigation"
        estimated_water_use_liters = drip_usage * field_size_hectares
        efficiency_rating = "High"
    elif 500 <= rainfall <= 1000:
        method = "Sprinkler Irrigation"
        estimated_water_use_liters = sprinkler_usage * field_size_hectares
        efficiency_rating = "Medium"
    else:
        method = "Optimized Flood Irrigation"
        estimated_water_use_liters = optimized_flood_usage * field_size_hectares
        efficiency_rating = "Low to Medium"
        
    return {
        "method": method,
        "estimated_water_use_liters": estimated_water_use_liters,
        "efficiency_rating": efficiency_rating
    }
