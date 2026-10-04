import logging

from fastapi import APIRouter
from src.api.schemas import PredictionRequest, PredictionResponse, ChatRequest, ChatResponse
from src.pipeline.orchestrator import run_pipeline
from src.core.config import GROQ_API_KEY
from src.core.dataset_stats import get_dataset_context
from src.db.database import log_prediction, recent_predictions, prediction_stats
from groq import Groq


router = APIRouter()
logger = logging.getLogger("agrosmart.endpoints")

@router.get("/health")
def api_health():
    return {"status": "healthy"}


@router.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    user_inputs = request.model_dump()
    pipeline_results = await run_pipeline(user_inputs)
    
    crop = pipeline_results["crop"]
    sust = pipeline_results["sustainability"]
    irr = pipeline_results["irrigation"]
    field_size = user_inputs["field_size_hectares"]
    
    confidence_pct = round(crop.get("confidence", 0.0) * 100, 1)
    logger.info("Prediction: crop=%s confidence=%.1f%% irrigation=%s", crop.get("top_recommendation"), confidence_pct, irr.get("method"))
    try:
        log_prediction(user_inputs, crop.get("top_recommendation", ""), confidence_pct, irr.get("method", ""))
    except Exception as e:  # logging must never break a prediction
        logger.warning("Could not save prediction to the database: %s", e)

    return PredictionResponse(
        recommended_crop=crop.get("top_recommendation", ""),
        confidence=round(crop.get("confidence", 0.0) * 100, 1),  # model gives 0-1, UI expects percent
        water_saved_liters_ha=round(sust.get("water_saved_liters", 0.0) / field_size, 1),
        green_impact_score=min(100, round(sust.get("water_saved_pct", 0.0) + 0.4 * confidence_pct)),
        crop_description=f"{crop.get('top_recommendation', '').capitalize()} is an excellent choice for your specific soil profile and climate.",
        top_crops=crop.get("top_crops", []),
        next_crop_rotation="Legumes",
        rotation_reason="Fixes nitrogen in the soil naturally, preparing it for the next season.",
        water_saved_pct=sust.get("water_saved_pct", 0.0),
        bathtubs_saved=int(sust.get("water_saved_liters", 0) / 150),
        carbon_reduced_kg_ha=sust.get("carbon_reduced_kg_ha", 0.0),
        km_not_driven=sust.get("km_not_driven", 0),
        irrigation_technique=irr.get("method", ""),
        sustainable_practices=["Implement crop rotation", "Use organic compost", "Monitor soil pH regularly"],
        feature_importances=crop.get("feature_importances", {}),
        model_accuracy_pct=crop.get("model_accuracy_pct", 98.66)
    )

@router.get("/history")
def history(limit: int = 10):
    return recent_predictions(max(1, min(limit, 100)))


@router.get("/stats")
def stats():
    return prediction_stats()


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
            model="openai/gpt-oss-20b",
            temperature=0.7,
            max_tokens=1000
        )
        reply = completion.choices[0].message.content or "No response generated. Please try again."
        return ChatResponse(reply=reply)
    except Exception as e:
        logger.error("Chat request to Groq failed: %s", e)
        return ChatResponse(reply=f"Error connecting to AgroBot AI: {str(e)}")
