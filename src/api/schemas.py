from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class PredictionRequest(BaseModel):
    N: float = Field(..., description="Nitrogen content in soil")
    P: float = Field(..., description="Phosphorous content in soil")
    K: float = Field(..., description="Potassium content in soil")
    temperature: float = Field(..., description="Temperature in Celsius")
    humidity: float = Field(..., description="Relative humidity in %")
    ph: float = Field(..., description="pH value of the soil")
    rainfall: float = Field(..., description="Rainfall in mm")
    field_size_hectares: float = Field(1.0, description="Field size in hectares")
    region: str = Field("Unknown", description="Region")
    season: str = Field("Unknown", description="Season")

class CropConfidence(BaseModel):
    crop: str
    confidence: float

class PredictionResponse(BaseModel):
    model_config = {'protected_namespaces': ()}
    
    recommended_crop: str
    confidence: float
    water_saved_liters_ha: float
    green_impact_score: int
    crop_description: str
    top_crops: List[CropConfidence]
    next_crop_rotation: str
    rotation_reason: str
    water_saved_pct: float
    bathtubs_saved: int
    carbon_reduced_kg_ha: float
    km_not_driven: int
    irrigation_technique: str
    sustainable_practices: List[str]
    feature_importances: Dict[str, float]
    model_accuracy_pct: float

class ChatRequest(BaseModel):
    message: str
    farm_context: Dict[str, Any]

class ChatResponse(BaseModel):
    reply: str
