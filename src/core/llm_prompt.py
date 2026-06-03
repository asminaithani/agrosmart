import os
import json
from groq import Groq
from src.core.config import GROQ_API_KEY

def format_response(crop: dict, sustainability: dict, irrigation: dict) -> str:
    if not GROQ_API_KEY or GROQ_API_KEY == "your_api_key_here":
        # Fallback if no API key
        return fallback_formatter(crop, sustainability, irrigation)
        
    client = Groq(api_key=GROQ_API_KEY)
    
    payload = {
        "crop": crop,
        "sustainability": sustainability,
        "irrigation": irrigation
    }
    
    system_prompt = """
    You are a Climate-Smart Agriculture Assistant. Translate the provided pipeline JSON into a friendly, supportive, and practical guide for a farmer.
    Use simple terms, provide encouragement, and organize the response clearly with emojis. Do not invent new technical data.
    
    CRITICAL INSTRUCTIONS FOR YOUR FORMAT:
    1. You MUST explicitly list the Top 1 Recommended Crop along with its Confidence/Accuracy percentage.
    2. You MUST explicitly list the 2 Alternative Crops as backups.
    3. Detail the recommended irrigation method and its expected water usage.
    4. Highlight the sustainable impact metrics (water saved, carbon reduction, emissions).
    
    Format your entire response in beautifully structured Markdown.
    """
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(payload)}
            ],
            model="llama-3.1-8b-instant",
            temperature=0.7,
            max_tokens=500
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Groq API Error: {e}")
        return fallback_formatter(crop, sustainability, irrigation)

def fallback_formatter(crop, sustainability, irrigation) -> str:
    return f"""
### 🌾 Crop Recommendation: {crop['top_recommendation'].capitalize()}
We are {int(crop['confidence']*100)}% confident in this recommendation. Alternatives: {', '.join(crop['alternatives'])}.

### 💧 Irrigation Plan: {irrigation['method']}
This method is highly recommended for your region.
- Estimated Water Use: {irrigation['estimated_water_use_liters']:,.0f} Liters
- Efficiency: {irrigation['efficiency_rating']}

### 🌱 Sustainability Impact
- Water Saved: {sustainability['water_saved_liters']:,.0f} Liters
- Carbon Reduction: {sustainability['carbon_reduction_pct']}%
- Expected Emission: {sustainability['emission_kg_per_season']} kg CO₂/kg yield
"""
