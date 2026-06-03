"""
app.py  —  AgroSmart AI  |  Streamlit Frontend
It runs with:  streamlit run src/frontend/app.py
Set AGROSMART_API_BASE_URL to backend API origin.
"""

import streamlit as st
import time, math

from mock_data import PRESETS
from services.api_client import ApiClientError, chat, predict_crop

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title  = "AgroSmart AI",
    page_icon   = "AgroSmart",
    layout      = "wide",
    initial_sidebar_state = "expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS  —  Clean, Minimalist, Premium Theme
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Outfit:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Root palette ── */
:root {
  --bg:          #0f172a;
  --surface:     #1e293b;
  --surface2:    #334155;
  --primary:     #10b981;
  --primary-dim: #065f46;
  --amber:       #f59e0b;
  --sky:         #0ea5e9;
  --red:         #ef4444;
  --text:        #f8fafc;
  --text-muted:  #94a3b8;
  --border:      #334155;
  --radius:      8px;
}

/* ── Base ── */
html, body, [data-testid="stAppViewContainer"] {
  background: var(--bg) !important;
  color: var(--text) !important;
  font-family: 'Inter', sans-serif !important;
}
[data-testid="stSidebar"] {
  background: var(--bg) !important;
  border-right: 1px solid var(--border) !important;
}
[data-testid="stHeader"] { background: transparent !important; }

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, [data-testid="stToolbar"] { visibility: hidden; }

/* ── Sidebar labels ── */
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stMarkdown p {
  color: var(--text-muted) !important;
  font-size: 0.75rem !important;
  letter-spacing: 0.05em !important;
  font-weight: 500 !important;
}

/* ── Sliders ── */
[data-testid="stSlider"] > div > div > div > div {
  background: var(--primary) !important;
}
[data-testid="stSlider"] [data-testid="stTickBar"] { display: none; }

/* ── Select boxes ── */
[data-testid="stSelectbox"] > div > div {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  color: var(--text) !important;
  border-radius: var(--radius) !important;
}

/* ── Primary button ── */
.stButton > button[kind="primary"] {
  background: var(--primary) !important;
  color: #ffffff !important;
  font-family: 'Outfit', sans-serif !important;
  font-size: 1.0rem !important;
  font-weight: 500 !important;
  border: none !important;
  border-radius: var(--radius) !important;
  padding: 0.5rem 1.5rem !important;
  width: 100% !important;
  transition: background 0.2s ease !important;
}
.stButton > button[kind="primary"]:hover {
  background: #059669 !important;
}

/* ── Secondary button ── */
.stButton > button:not([kind="primary"]) {
  background: transparent !important;
  color: var(--text-muted) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 0.85rem !important;
  transition: all 0.2s ease !important;
}
.stButton > button:not([kind="primary"]):hover {
  border-color: var(--primary) !important;
  color: var(--primary) !important;
}

/* ── Chat input ── */
[data-testid="stChatInput"] textarea {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  color: var(--text) !important;
  border-radius: var(--radius) !important;
  font-family: 'Inter', sans-serif !important;
}

/* ── Chat messages ── */
[data-testid="stChatMessage"] {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  margin-bottom: 0.5rem !important;
}

/* ── Divider ── */
hr { border-color: var(--border) !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--surface2); border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# HELPER COMPONENTS
# ─────────────────────────────────────────────────────────────────────────────

def card(content_html: str, accent: str = "#10b981", padding: str = "1.4rem"):
    st.markdown(f"""
    <div style="
        background:var(--surface);
        border:1px solid var(--border);
        border-top:2px solid {accent};
        border-radius:var(--radius);
        padding:{padding};
        margin-bottom:0.8rem;
    ">{content_html}</div>""", unsafe_allow_html=True)

def stat_block(label, value, unit="", color="#10b981"):
    st.markdown(f"""
    <div style="
        background:var(--surface);
        border:1px solid var(--border);
        border-radius:var(--radius);
        padding:1.2rem;
        text-align:left;
        height:100%;
    ">
      <div style="font-size:0.75rem;color:var(--text-muted);text-transform:uppercase;
                  letter-spacing:0.05em;margin-bottom:4px;font-weight:500">{label}</div>
      <div style="font-family:'Outfit', sans-serif;font-size:1.8rem;color:{color};
                  line-height:1;font-weight:600">{value}</div>
      <div style="font-size:0.75rem;color:var(--text-muted);
                  margin-top:6px">{unit}</div>
    </div>""", unsafe_allow_html=True)

def gis_gauge(score: float):
    score = max(0, min(100, score))
    color = "#10b981" if score >= 70 else "#f59e0b" if score >= 40 else "#ef4444"
    label = "Optimal" if score >= 70 else "Fair" if score >= 40 else "Critical"
    fill = score * 1.8

    st.markdown(f"""
    <div style="width:100%;display:flex;justify-content:center;margin-top:1rem;margin-bottom:0.5rem">
      <div style="position:relative;width:200px;height:110px;overflow:hidden">
        <div style="
          width:200px;height:200px;border-radius:50%;
          background:conic-gradient(from 270deg, {color} 0deg {fill:.1f}deg,
                     var(--border) {fill:.1f}deg 180deg, transparent 180deg 360deg);
        "></div>
        <div style="
          position:absolute;left:10px;top:10px;width:180px;height:180px;
          border-radius:50%;background:var(--surface);
        "></div>
        <div style="
          position:absolute;left:0;right:0;top:45px;text-align:center;
          font-family:'Outfit',sans-serif;font-size:2.2rem;color:var(--text);
          font-weight:600;line-height:1;
        ">{score:.1f}</div>
        <div style="
          position:absolute;left:0;right:0;top:85px;text-align:center;
          font-size:0.7rem;color:{color};font-weight:500;
          text-transform:uppercase;
        ">{label}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

def confidence_bars(top_crops):
    bars_html = ""
    colors = ["#10b981", "#0ea5e9", "#f59e0b"]
    for i, crop in enumerate(top_crops):
        pct   = crop['confidence']
        color = colors[i]
        bars_html += f"""
        <div style="margin-bottom:12px">
          <div style="display:flex;justify-content:space-between;
                      font-size:0.8rem;margin-bottom:6px">
            <span style="color:var(--text);text-transform:capitalize;
                         font-weight:{'600' if i==0 else '400'}">
              {crop['crop']}
            </span>
            <span style="color:var(--text-muted);font-family:'JetBrains Mono',monospace">{pct:.1f}%</span>
          </div>
          <div style="background:var(--surface2);border-radius:4px;height:4px;overflow:hidden">
            <div style="width:{pct}%;height:100%;background:{color};border-radius:4px;
                        transition:width 0.8s ease"></div>
          </div>
        </div>"""
    return bars_html

def feature_importance_chart(fi: dict):
    labels = {"N":"Nitrogen","P":"Phosphorus","K":"Potassium",
              "temperature":"Temperature","humidity":"Humidity",
              "ph":"Soil pH","rainfall":"Rainfall"}
    sorted_fi = sorted(feature_importances.items(), key=lambda x: x[1], reverse=True)

    if not sorted_fi:
     st.warning("No feature importance data available")
    return
    max_val = sorted_fi[0][1]
    bars_html = ""
    for key, val in sorted_fi:
        pct   = (val / max_val) * 100
        label = labels.get(key, key)
        bars_html += f"""
        <div style="margin-bottom:10px">
          <div style="display:flex;justify-content:space-between;font-size:0.75rem;
                      margin-bottom:4px">
            <span style="color:var(--text-muted)">{label}</span>
            <span style="color:var(--sky);font-family:'JetBrains Mono',monospace">{val:.3f}</span>
          </div>
          <div style="background:var(--surface2);border-radius:2px;height:4px">
            <div style="width:{pct:.1f}%;height:100%;border-radius:2px;
                        background:var(--sky)"></div>
          </div>
        </div>"""
    return bars_html

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
if "result"   not in st.session_state: st.session_state.result   = None
if "messages" not in st.session_state: st.session_state.messages = []
if "analyzed" not in st.session_state: st.session_state.analyzed = False

# ─────────────────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="
  display:flex; align-items:center; gap:16px;
  padding:1rem 0; border-bottom:1px solid var(--border);
  margin-bottom:1.5rem;
">
  <div>
    <div style="
      font-family:'Outfit',sans-serif; font-size:1.8rem; font-weight:600;
      color:var(--text); letter-spacing:0.02em; line-height:1;
    ">AgroSmart Platform</div>
    <div style="font-size:0.8rem; color:var(--text-muted); margin-top:4px">
      Climate-Smart Agriculture Analytics & Optimization
    </div>
  </div>
  <div style="margin-left:auto; text-align:right">
    <div style="
      background:transparent; border:1px solid var(--primary-dim);
      border-radius:4px; padding:4px 10px;
      font-size:0.7rem; color:var(--primary);
      font-family:'JetBrains Mono',monospace; font-weight:500;
    ">SYSTEM ONLINE</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR  —  Input Form
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="
      font-family:'Outfit',sans-serif; font-size:1.1rem; font-weight:600;
      color:var(--text); padding:0.4rem 0 1rem 0;
      border-bottom:1px solid var(--border); margin-bottom:1rem;
    ">Configuration Parameters</div>
    """, unsafe_allow_html=True)

    st.markdown("<p style='color:var(--text-muted);font-size:0.7rem;margin-bottom:1rem;text-transform:uppercase'>Soil Nutrients (kg/ha)</p>", unsafe_allow_html=True)
    N = st.slider("Nitrogen (N)",        0,   200, 90)
    P = st.slider("Phosphorus (P)",      5,   145, 42)
    K = st.slider("Potassium (K)",       5,   205, 43)

    st.markdown("<p style='color:var(--text-muted);font-size:0.7rem;margin:1rem 0 0.5rem;text-transform:uppercase'>Environmental Data</p>", unsafe_allow_html=True)
    temperature = st.slider("Temperature (°C)", 8.0,  44.0, 25.0, 0.1)
    humidity    = st.slider("Humidity (%)",     14.0, 100.0, 82.0, 0.1)
    rainfall    = st.slider("Rainfall (mm)",    20.0, 300.0, 200.0, 1.0)

    st.markdown("<p style='color:var(--text-muted);font-size:0.7rem;margin:1rem 0 0.5rem;text-transform:uppercase'>Soil Chemistry</p>", unsafe_allow_html=True)
    ph = st.slider("Soil pH",               3.5, 9.5, 6.5, 0.1)

    st.markdown("<p style='color:var(--text-muted);font-size:0.7rem;margin:1rem 0 0.5rem;text-transform:uppercase'>Metadata</p>", unsafe_allow_html=True)
    region = st.selectbox("Region", ["Punjab","Uttar Pradesh","Maharashtra",
                                     "Karnataka","Tamil Nadu","West Bengal",
                                     "Rajasthan","Madhya Pradesh","Andhra Pradesh","Bihar"])
    season = st.selectbox("Season", ["Kharif (June–Oct)","Rabi (Nov–Mar)","Zaid (Mar–Jun)"])

    st.markdown("<br>", unsafe_allow_html=True)
    analyze_btn = st.button("Generate Analysis", type="primary")

    # Quick presets
    st.markdown("<p style='color:var(--text-muted);font-size:0.7rem;margin:1.2rem 0 0.4rem;text-transform:uppercase'>Load Presets</p>", unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    rice_preset  = col_a.button("Rice",   use_container_width=True)
    wheat_preset = col_b.button("Wheat",  use_container_width=True)
    col_c, col_d = st.columns(2)
    mango_preset  = col_c.button("Mango",  use_container_width=True)
    maize_preset  = col_d.button("Maize",  use_container_width=True)

# Apply preset (rebuild sidebar values via session state workaround — use API call directly)
preset_data = None
if rice_preset:  preset_data = PRESETS["rice"]
if wheat_preset: preset_data = PRESETS["wheat"]
if mango_preset: preset_data = PRESETS["mango"]
if maize_preset: preset_data = PRESETS["maize"]

# ─────────────────────────────────────────────────────────────────────────────
# BACKEND CALL
# ─────────────────────────────────────────────────────────────────────────────
def call_predict(payload: dict):
    try:
        return predict_crop(payload), None
    except ApiClientError as e:
        return None, f"System Error: {e}"

if analyze_btn or preset_data is not None:
    if preset_data:
        payload = {**preset_data, "region": region, "season": season}
    else:
        payload = dict(N=N, P=P, K=K, temperature=temperature,
                       humidity=humidity, ph=ph, rainfall=rainfall,
                       region=region, season=season)

    with st.spinner("Processing telemetry..."):
        time.sleep(0.4)
        result, err = call_predict(payload)

    if err:
        st.error(err)
    else:
        st.session_state.result   = result
        st.session_state.analyzed = True
        st.session_state.payload  = payload

# ─────────────────────────────────────────────────────────────────────────────
# MAIN  —  Results Dashboard
# ─────────────────────────────────────────────────────────────────────────────
if not st.session_state.analyzed:
    # ── Welcome / empty state ──
    st.markdown("""
    <div style="
      text-align:center; padding:5rem 2rem;
      border:1px dashed var(--border); border-radius:var(--radius);
      background:var(--surface);
    ">
      <div style="font-family:'Outfit',sans-serif;font-size:1.4rem;font-weight:500;color:var(--text);
                  margin-bottom:0.5rem">Awaiting Telemetry Data</div>
      <div style="color:var(--text-muted);font-size:0.9rem;max-width:420px;
                  margin-left:auto;margin-right:auto">
        Configure farm parameters in the sidebar and initialize analysis to view predictive intelligence and sustainability metrics.
      </div>
      <div style="margin-top:2.5rem;display:flex;justify-content:center;gap:3rem;
                  flex-wrap:wrap">
        <div style="text-align:center;color:var(--text-muted);font-size:0.8rem">
          <div style="font-weight:600;color:var(--text);margin-bottom:4px">ML Inference</div>
          RandomForest Pipeline
        </div>
        <div style="text-align:center;color:var(--text-muted);font-size:0.8rem">
          <div style="font-weight:600;color:var(--text);margin-bottom:4px">Water Efficiency</div>
          Consumption Analytics
        </div>
        <div style="text-align:center;color:var(--text-muted);font-size:0.8rem">
          <div style="font-weight:600;color:var(--text);margin-bottom:4px">Sustainability</div>
          Carbon Footprint Tracking
        </div>
        <div style="text-align:center;color:var(--text-muted);font-size:0.8rem">
          <div style="font-weight:600;color:var(--text);margin-bottom:4px">LLM Advisor</div>
          Conversational Interface
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

else:
    r = st.session_state.result

    # ── TOP ROW: 4 quick stats ────────────────────────────────────────────────
    q1, q2, q3, q4 = st.columns(4)
    with q1:
        stat_block("Primary Recommendation", r["recommended_crop"].capitalize(), color="var(--primary)")
    with q2:
        stat_block("Inference Confidence", f"{r['confidence']:.1f}%", unit="Model Certainty", color="var(--sky)")
    with q3:
        stat_block("Water Conservation", f"{r['water_saved_liters_ha']:,}", unit="Liters / Hectare", color="var(--sky)")
    with q4:
        gis_color = "var(--primary)" if r["green_impact_score"] >= 70 else "var(--amber)" if r["green_impact_score"] >= 40 else "var(--red)"
        stat_block("Sustainability Index", f"{r['green_impact_score']}", unit="Score (0-100)", color=gis_color)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── MAIN ROW: 3 columns ───────────────────────────────────────────────────
    left, mid, right = st.columns([1.1, 1.2, 1.0])

    # ────────── LEFT: Crop Prediction ────────────────────────────────────────
    with left:
        st.markdown(f"""
        <div style="
            background:var(--surface);
            border:1px solid var(--border);
            border-top:2px solid var(--primary);
            border-radius:var(--radius);
            padding:1.4rem;
            margin-bottom:0.8rem;
        ">
          <div style="font-size:0.75rem;color:var(--text-muted);
                      text-transform:uppercase;margin-bottom:12px;font-weight:500">
            Prediction Analysis
          </div>
          <div style="font-family:'Outfit',sans-serif;font-size:2rem;color:var(--text);
                      font-weight:600;line-height:1;margin-bottom:8px">
            {r['recommended_crop'].capitalize()}
          </div>
          <div style="font-size:0.85rem;color:var(--text-muted);margin-bottom:20px;line-height:1.5">
            {r['crop_description']}
          </div>
          <div style="font-size:0.7rem;color:var(--text-muted);
                      text-transform:uppercase;margin-bottom:12px;font-weight:500">Candidate Probabilities</div>
          {confidence_bars(r['top_crops'])}
        </div>
        """, unsafe_allow_html=True)

        card(f"""
        <div style="font-size:0.75rem;color:var(--text-muted);
                    text-transform:uppercase;margin-bottom:10px;font-weight:500">
          Rotation Intelligence
        </div>
        <div style="font-size:0.9rem;color:var(--text);margin-bottom:6px">
          Suggested Next Crop:
          <strong style="color:var(--amber);text-transform:capitalize;font-weight:500">
            &nbsp;{r['next_crop_rotation']}
          </strong>
        </div>
        <div style="font-size:0.8rem;color:var(--text-muted);line-height:1.5">{r['rotation_reason']}</div>
        """, accent="var(--amber)")

    # ────────── MIDDLE: Sustainability Dashboard ──────────────────────────────
    with mid:
        st.markdown("""
        <div style="
            background:var(--surface);
            border:1px solid var(--border);
            border-top:2px solid var(--amber);
            border-radius:var(--radius);
            padding:1.4rem;
            margin-bottom:0.8rem;
        ">
          <div style="font-size:0.75rem;color:var(--text-muted);
                      text-transform:uppercase;margin-bottom:8px;font-weight:500">
            Environmental Impact
          </div>
        """, unsafe_allow_html=True)
        gis_gauge(r["green_impact_score"])
        st.markdown("</div>", unsafe_allow_html=True)

        # Water + Carbon split
        w_col, c_col = st.columns(2)
        with w_col:
            stat_block("Efficiency", f"{r['water_saved_pct']}%", unit=f"{r['bathtubs_saved']:,} bathtubs equivalent", color="var(--sky)")
        with c_col:
            stat_block("CO₂ Offset", f"{r['carbon_reduced_kg_ha']}", unit=f"kg/ha ({r['km_not_driven']:,} km)", color="var(--primary)")

        # Irrigation technique badge
        st.markdown(f"""
        <div style="
          background:var(--surface);
          border:1px solid var(--border); border-radius:var(--radius);
          padding:1.2rem; margin-top:0.8rem;
        ">
          <div style="font-size:0.75rem;color:var(--text-muted);
                      text-transform:uppercase;font-weight:500;margin-bottom:4px">Optimized Irrigation</div>
          <div style="font-size:1.1rem;color:var(--text);font-weight:500;
                      margin-bottom:4px">{r['irrigation_technique']}</div>
          <div style="font-size:0.8rem;color:var(--sky)">
            Saves {r['water_saved_pct']}% water volume compared to conventional methods.
          </div>
        </div>
        """, unsafe_allow_html=True)

    # ────────── RIGHT: Practices + Explainability ─────────────────────────────
    with right:
        practices_html = "".join([
            f'<div style="display:flex;align-items:flex-start;gap:10px;'
            f'margin-bottom:8px;padding:10px 12px;background:var(--surface2);'
            f'border-radius:6px;border-left:2px solid var(--primary)">'
            f'<span style="font-size:0.85rem;color:var(--text);line-height:1.4">{p}</span>'
            f'</div>'
            for p in r["sustainable_practices"]
        ])
        card(f"""
        <div style="font-size:0.75rem;color:var(--text-muted);
                    text-transform:uppercase;margin-bottom:12px;font-weight:500">
          Recommended Protocols
        </div>
        {practices_html}
        """, accent="var(--primary-dim)")

        st.markdown(f"""
        <div style="
            background:var(--surface);
            border:1px solid var(--border);
            border-top:2px solid var(--sky);
            border-radius:var(--radius);
            padding:1.4rem;
            margin-bottom:0.8rem;
        ">
          <div style="font-size:0.75rem;color:var(--text-muted);
                      text-transform:uppercase;margin-bottom:12px;font-weight:500">
            Model Explainability
          </div>
          {feature_importance_chart(r['feature_importances'])}
          <div style="font-size:0.75rem;color:var(--text-muted);margin-top:12px;text-align:right">
            Validation Accuracy: {r['model_accuracy_pct']}%
          </div>
        </div>
        """, unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────────
    # INPUT SUMMARY STRIP
    # ─────────────────────────────────────────────────────────────────────────
    p = st.session_state.payload
    summary_items_html = ''.join([
        f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:0.8rem;'
        f'color:var(--text)"><span style="color:var(--text-muted)">{k.upper()}</span> {v}</span>'
        for k, v in [("N",p["N"]),("P",p["P"]),("K",p["K"]),
                     ("Temp",f"{p['temperature']}°C"),
                     ("Humidity",f"{p['humidity']}%"),
                     ("pH",p["ph"]),
                     ("Rainfall",f"{p['rainfall']}mm"),
                     ("Region",p["region"]),
                     ("Season",p["season"])]
    ])
    
    st.markdown(f"""
    <div style="
      background:var(--surface); border:1px solid var(--border);
      border-radius:var(--radius); padding:1rem 1.4rem;
      display:flex; flex-wrap:wrap; gap:1.5rem; align-items:center;
      margin:0.6rem 0 1.2rem;
    ">
      <span style="font-size:0.75rem;color:var(--text-muted);
                   text-transform:uppercase;font-weight:500">Active Profile</span>
      {summary_items_html}
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# CHATBOT SECTION
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="
  font-family:'Outfit',sans-serif; font-size:1.2rem; font-weight:600; color:var(--text);
  padding:1rem 0 0.5rem; border-top:1px solid var(--border); margin-top:1rem;
">Analytic Assistant Interface</div>
<div style="font-size:0.85rem;color:var(--text-muted);margin-bottom:1.5rem">
  Natural language queries regarding sustainability, agronomy, or prediction rationale.
</div>
""", unsafe_allow_html=True)

chat_col, tip_col = st.columns([2.2, 1])

with chat_col:
    # Chat history
    chat_box = st.container()
    with chat_box:
        if not st.session_state.messages:
            st.markdown("""
            <div style="
              text-align:center; padding:2rem;
              border:1px dashed var(--border); border-radius:var(--radius);
              color:var(--text-muted); font-size:0.9rem; background:var(--surface);
            ">
              System initialized. Awaiting user input.
            </div>
            """, unsafe_allow_html=True)

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # Chat input
    if prompt := st.chat_input("Enter your query here..."):
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Call backend /chat
        farm_ctx = st.session_state.result or {}
        try:
            reply = chat(prompt, farm_ctx).get("reply", "System fault: Query unprocessable.")
        except ApiClientError:
            reply = "Backend connection failed. System offline."

        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()

with tip_col:
    st.markdown("""
    <div style="
      background:var(--surface); border:1px solid var(--border);
      border-radius:var(--radius); padding:1.2rem;
    ">
      <div style="font-size:0.75rem;color:var(--text-muted);
                  text-transform:uppercase;margin-bottom:12px;font-weight:500">
        Suggested Queries
      </div>
    """, unsafe_allow_html=True)

    suggestions = [
        "What irrigation saves the most water?",
        "How can I reduce my carbon footprint?",
        "Explain the rotation intelligence output.",
        "How to improve soil nutrient distribution?",
        "Provide sustainable pest management protocols.",
        "Breakdown the Green Impact Score.",
    ]
    for s in suggestions:
        if st.button(s, use_container_width=True, key=f"sug_{s[:10]}"):
            st.session_state.messages.append({"role": "user", "content": s})
            farm_ctx = st.session_state.result or {}
            try:
                reply = chat(s, farm_ctx).get("reply", "System fault: Query unprocessable.")
            except ApiClientError:
                reply = "Backend connection failed. System offline."
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    # Clear chat
    if st.session_state.messages:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Clear Interface Log", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="
  border-top:1px solid var(--border); margin-top:3rem; padding:1.5rem 0;
  display:flex; justify-content:space-between; align-items:center;
  flex-wrap:wrap; gap:0.5rem;
">
  <div style="font-size:0.75rem;color:var(--text-muted)">
    AgroSmart Analytics Platform  ·  v2.0
  </div>
  <div style="font-size:0.75rem;color:var(--text-muted);font-family:'JetBrains Mono',monospace">
    Powered by RandomForest & FastAPI
  </div>
</div>
""", unsafe_allow_html=True)
