from fastapi import APIRouter, HTTPException
from src.api.schemas import PredictionRequest, PredictionResponse, ChatRequest, ChatResponse
from src.pipeline.orchestrator import run_pipeline
from src.core.config import GROQ_API_KEY
from src.core.dataset_stats import get_dataset_context
from groq import Groq


router = APIRouter()

@router.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    user_inputs = request.model_dump()
    pipeline_results = await run_pipeline(user_inputs)
    
    crop = pipeline_results["crop"]
    sust = pipeline_results["sustainability"]
    irr = pipeline_results["irrigation"]
    
    return PredictionResponse(
        recommended_crop=crop.get("top_recommendation", ""),
        confidence=crop.get("confidence", 0.0),
        water_saved_liters_ha=sust.get("water_saved_liters", 0.0),
        green_impact_score=85, # dynamic mock
        crop_description=f"{crop.get('top_recommendation', '').capitalize()} is an excellent choice for your specific soil profile and climate.",
        top_crops=crop.get("top_crops", []),
        next_crop_rotation="Legumes",
        rotation_reason="Fixes nitrogen in the soil naturally, preparing it for the next season.",
        water_saved_pct=sust.get("carbon_footprint_reduction_pct", 40.0), # mapped loosely
        bathtubs_saved=int(sust.get("water_saved_liters", 0) / 150),
        carbon_reduced_kg_ha=1.1,
        km_not_driven=5,
        irrigation_technique=irr.get("method", ""),
        sustainable_practices=["Implement crop rotation", "Use organic compost", "Monitor soil pH regularly"],
        feature_importances=crop.get("feature_importances", {}),
        model_accuracy_pct=crop.get("model_accuracy_pct", 98.66)
    )

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not GROQ_API_KEY or GROQ_API_KEY == "your_groq_api_key_here":
        return ChatResponse(reply="API key missing. I'm AgroBot, how can I help you?")
        
    client = Groq(api_key=GROQ_API_KEY)
    
    dataset_context = get_dataset_context()
    system_prompt = f"You are AgroSmart Analytics AI. Maintain a professional, analytical, and enterprise-grade tone. Do NOT use any emojis. Keep your answers brief and concise.\n\n{dataset_context}"
    context_str = f"Farm Context: {request.farm_context}"
    
    try:
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt + "\n" + context_str},
                {"role": "user", "content": request.message}
            ],
            model="llama-3.1-8b-instant",
            temperature=0.7,
            max_tokens=300
        )
        reply = completion.choices[0].message.content
        return ChatResponse(reply=reply)
    except Exception as e:
        return ChatResponse(reply=f"Error connecting to AgroBot AI: {str(e)}")
