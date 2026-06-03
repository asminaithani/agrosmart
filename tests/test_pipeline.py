import pytest
import asyncio
from src.pipeline.sustainability import calculate_sustainability
from src.pipeline.irrigation import recommend_irrigation

@pytest.mark.asyncio
async def test_calculate_sustainability():
    crop_data = {"top_recommendation": "rice"}
    user_inputs = {"field_size_hectares": 2.0, "rainfall": 400.0}
    
    result = await calculate_sustainability(crop_data, user_inputs)
    
    # Expected: drip_usage = 6000, baseline = 15000, savings = 9000 * 2 = 18000
    assert result["water_saved_liters"] == 18000.0
    assert result["carbon_reduction_pct"] > 0
    assert result["emission_kg_per_season"] == 1.4

@pytest.mark.asyncio
async def test_recommend_irrigation():
    crop_data = {"top_recommendation": "rice"}
    user_inputs = {"field_size_hectares": 2.0, "rainfall": 400.0}
    
    result = await recommend_irrigation(crop_data, user_inputs)
    
    # Expected: rainfall < 500 & crop is rice -> Drip Irrigation
    assert result["method"] == "Drip Irrigation"
    assert result["estimated_water_use_liters"] == 12000.0  # 6000 * 2
    assert result["efficiency_rating"] == "High"

@pytest.mark.asyncio
async def test_recommend_irrigation_sprinkler():
    crop_data = {"top_recommendation": "wheat"}
    user_inputs = {"field_size_hectares": 1.0, "rainfall": 600.0}
    
    result = await recommend_irrigation(crop_data, user_inputs)
    
    assert result["method"] == "Sprinkler Irrigation"
    assert result["estimated_water_use_liters"] == 9000.0
