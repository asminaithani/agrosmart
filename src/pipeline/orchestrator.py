import asyncio
from typing import Dict, Any
from src.ml.predict import predict_crop_sync
from src.pipeline.sustainability import calculate_sustainability
from src.pipeline.irrigation import recommend_irrigation

async def predict_crop(user_inputs: Dict[str, Any]) -> Dict[str, Any]:
    return await asyncio.to_thread(predict_crop_sync, user_inputs)

async def run_pipeline(user_inputs: Dict[str, Any]) -> Dict[str, Any]:
    # STEP 1
    crop_data = await predict_crop(user_inputs)
    
    # STEP 2 & 3
    sustainability, irrigation = await asyncio.gather(
        calculate_sustainability(crop_data, user_inputs),
        recommend_irrigation(crop_data, user_inputs)
    )
    
    return {
        "crop": crop_data,
        "sustainability": sustainability,
        "irrigation": irrigation
    }
