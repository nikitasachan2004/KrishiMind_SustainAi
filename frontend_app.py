"""
KrishiMind SustainAI — Crop Planning & Optimization Engine
Streamlit Frontend Dashboard

Single-file frontend that connects to the KrishiMind SustainAI API.
No local model access — API only.
"""

import streamlit as st
import requests
import pandas as pd
from typing import Dict, Any, Optional

# =============================================================================
# CONFIGURATION
# =============================================================================

API_BASE_URL = "http://127.0.0.1:8000"
API_TIMEOUT = 20  # seconds

# Season options
SEASONS = ["Kharif", "Rabi", "Summer", "Autumn", "Winter", "Whole Year"]

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="KrishiMind SustainAI — Crop Planning",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# CUSTOM CSS FOR BETTER STYLING
# =============================================================================

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1B5E20;
        text-align: center;
        padding: 1rem 0;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%);
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .risk-low { color: #2E7D32; font-weight: bold; }
    .risk-medium { color: #F57C00; font-weight: bold; }
    .risk-high { color: #C62828; font-weight: bold; }
    .api-connected { 
        background-color: #E8F5E9; 
        color: #2E7D32; 
        padding: 0.5rem 1rem; 
        border-radius: 20px;
        font-weight: 600;
    }
    .api-disconnected { 
        background-color: #FFEBEE; 
        color: #C62828; 
        padding: 0.5rem 1rem; 
        border-radius: 20px;
        font-weight: 600;
    }
    .stDataFrame {
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# API HELPER FUNCTIONS
# =============================================================================

def check_api_health() -> bool:
    """
    Check if the API is reachable and healthy.
    Returns True if connected, False otherwise.
    """
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get("status") == "healthy"
        return False
    except requests.exceptions.RequestException:
        return False


def call_crop_prediction_api(
    district: str,
    season: str,
    area: float,
    rainfall_delta: float,
    temp_delta: float
) -> Dict[str, Any]:
    """
    Call the crop prediction API endpoint.
    
    Args:
        district: District name
        season: Growing season
        area: Area in hectares
        rainfall_delta: Rainfall change (-1 to 1)
        temp_delta: Temperature change in °C
    
    Returns:
        API response as dictionary
    
    Raises:
        requests.exceptions.RequestException on API error
    """
    payload = {
        "district": district,
        "season": season,
        "area": area,
        "scenario": {
            "rainfall_delta": rainfall_delta,
            "temp_delta": temp_delta
        }
    }
    
    response = requests.post(
        f"{API_BASE_URL}/predict/crop-plan",
        json=payload,
        timeout=API_TIMEOUT
    )
    response.raise_for_status()
    return response.json()


def get_risk_color(score: float) -> str:
    """Get risk level color based on score."""
    if score <= 0.3:
        return "green"
    elif score <= 0.6:
        return "orange"
    else:
        return "red"


def get_risk_label(score: float) -> str:
    """Get risk level label based on score."""
    if score <= 0.3:
        return "🟢 Low Risk"
    elif score <= 0.6:
        return "🟠 Medium Risk"
    else:
        return "🔴 High Risk"

# =============================================================================
# HEADER
# =============================================================================

st.markdown('<h1 class="main-header">🌾 KrishiMind SustainAI</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Crop Planning & Resource Optimization Engine</p>', unsafe_allow_html=True)

# =============================================================================
# API HEALTH CHECK (ON STARTUP)
# =============================================================================

api_healthy = check_api_health()

col_status, col_spacer = st.columns([1, 3])
with col_status:
    if api_healthy:
        st.markdown('<span class="api-connected">✅ API Connected</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="api-disconnected">❌ API Not Reachable</span>', unsafe_allow_html=True)

st.markdown("---")

# =============================================================================
# SIDEBAR INPUTS
# =============================================================================

st.sidebar.header("🎯 Input Parameters")

# District input
district = st.sidebar.text_input(
    "District Name",
    value="Guntur",
    help="Enter the district name (e.g., Guntur, Nagpur, Pune)"
)

# Season dropdown
season = st.sidebar.selectbox(
    "Growing Season",
    options=SEASONS,
    index=0,
    help="Select the agricultural season"
)

# Area input
area = st.sidebar.number_input(
    "Area (Hectares)",
    min_value=0.1,
    max_value=10000.0,
    value=10.0,
    step=0.5,
    help="Enter the farm area in hectares"
)

st.sidebar.markdown("---")
st.sidebar.subheader("🌦️ Climate Scenario")

# Rainfall delta slider
rainfall_delta_pct = st.sidebar.slider(
    "Rainfall Change (%)",
    min_value=-40,
    max_value=40,
    value=0,
    step=5,
    help="Adjust expected rainfall (-40% drought to +40% excess)"
)
rainfall_delta = rainfall_delta_pct / 100.0  # Convert to fraction

# Temperature delta slider
temp_delta = st.sidebar.slider(
    "Temperature Change (°C)",
    min_value=-5.0,
    max_value=5.0,
    value=0.0,
    step=0.5,
    help="Adjust expected temperature change"
)

st.sidebar.markdown("---")

# Run button
run_optimization = st.sidebar.button(
    "🚀 Run Crop Optimization",
    type="primary",
    use_container_width=True,
    disabled=not api_healthy
)

# =============================================================================
# MAIN CONTENT AREA
# =============================================================================

if not api_healthy:
    st.error("""
    ⚠️ **API Not Available**
    
    The KrishiMind SustainAI backend is not reachable. Please ensure:
    1. The API server is running on `http://127.0.0.1:8000`
    2. Run: `uvicorn cloud.api.app:app --host 127.0.0.1 --port 8000`
    """)
    st.stop()

# =============================================================================
# API CALL AND RESULTS
# =============================================================================

if run_optimization:
    # Validate inputs
    if not district.strip():
        st.error("❌ Please enter a district name.")
        st.stop()
    
    if area <= 0:
        st.error("❌ Area must be greater than 0.")
        st.stop()
    
    # Call API with spinner
    with st.spinner("🔄 Running crop optimization... Please wait."):
        try:
            result = call_crop_prediction_api(
                district=district.strip(),
                season=season,
                area=area,
                rainfall_delta=rainfall_delta,
                temp_delta=temp_delta
            )
            
            # Store result in session state
            st.session_state["result"] = result
            st.session_state["inputs"] = {
                "district": district,
                "season": season,
                "area": area,
                "rainfall_delta_pct": rainfall_delta_pct,
                "temp_delta": temp_delta
            }
            
        except requests.exceptions.Timeout:
            st.error("⏱️ **Request Timeout** — The API took too long to respond. Please try again.")
            st.stop()
        except requests.exceptions.HTTPError as e:
            st.error(f"🚫 **API Error** — {e.response.status_code}: {e.response.text}")
            st.stop()
        except requests.exceptions.RequestException as e:
            st.error(f"🔌 **Connection Error** — Could not reach the API: {str(e)}")
            st.stop()

# =============================================================================
# DISPLAY RESULTS (IF AVAILABLE)
# =============================================================================

if "result" in st.session_state:
    result = st.session_state["result"]
    inputs = st.session_state["inputs"]
    
    st.success(f"✅ Optimization complete for **{result.get('district', 'N/A')}** — **{result.get('season', 'N/A')}** season")
    
    # -------------------------------------------------------------------------
    # SCENARIO SUMMARY
    # -------------------------------------------------------------------------
    st.subheader("📊 Scenario Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="District",
            value=result.get("district", "N/A")
        )
    
    with col2:
        st.metric(
            label="Season",
            value=result.get("season", "N/A")
        )
    
    with col3:
        st.metric(
            label="Area",
            value=f"{result.get('area_hectares', 0):.1f} ha"
        )
    
    with col4:
        st.metric(
            label="Scenario",
            value=result.get("scenario_applied", "baseline").replace("_", " ").title()
        )
    
    # Climate adjustments
    col_rain, col_temp = st.columns(2)
    with col_rain:
        rain_pct = inputs.get("rainfall_delta_pct", 0)
        rain_icon = "🌧️" if rain_pct > 0 else "☀️" if rain_pct < 0 else "🌤️"
        st.info(f"{rain_icon} **Rainfall Delta:** {rain_pct:+d}%")
    
    with col_temp:
        temp_val = inputs.get("temp_delta", 0)
        temp_icon = "🔥" if temp_val > 0 else "❄️" if temp_val < 0 else "🌡️"
        st.info(f"{temp_icon} **Temperature Delta:** {temp_val:+.1f}°C")
    
    st.markdown("---")
    
    # -------------------------------------------------------------------------
    # TOP CROPS TABLE
    # -------------------------------------------------------------------------
    st.subheader("🏆 Top Crop Recommendations")
    
    recommendations = result.get("recommendations", [])
    
    if recommendations:
        # Create DataFrame for display
        df_data = []
        for rec in recommendations:
            df_data.append({
                "Rank": f"#{rec.get('rank', 'N/A')}",
                "Crop": rec.get("crop", "N/A"),
                "Score": f"{rec.get('composite_score', 0):.3f}",
                "Yield (t/ha)": f"{rec.get('predicted_yield_tonnes_per_ha', 0):.2f}",
                "Price (₹/t)": f"₹{rec.get('predicted_price_inr_per_tonne', 0):,.0f}",
                "Revenue/ha": f"₹{rec.get('expected_revenue_inr_per_ha', 0):,.0f}",
                "Total Revenue": f"₹{rec.get('total_revenue_inr', 0):,.0f}",
                "Risk": rec.get("risk_level", "N/A").upper()
            })
        
        df = pd.DataFrame(df_data)
        
        # Display as styled dataframe
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Rank": st.column_config.TextColumn("Rank", width="small"),
                "Crop": st.column_config.TextColumn("Crop", width="medium"),
                "Score": st.column_config.TextColumn("Score", width="small"),
                "Yield (t/ha)": st.column_config.TextColumn("Yield (t/ha)", width="small"),
                "Price (₹/t)": st.column_config.TextColumn("Price (₹/t)", width="medium"),
                "Revenue/ha": st.column_config.TextColumn("Revenue/ha", width="medium"),
                "Total Revenue": st.column_config.TextColumn("Total Revenue", width="medium"),
                "Risk": st.column_config.TextColumn("Risk", width="small")
            }
        )
        
        st.markdown("---")
        
        # ---------------------------------------------------------------------
        # VISUALIZATIONS
        # ---------------------------------------------------------------------
        st.subheader("📈 Visual Analysis")
        
        col_chart1, col_chart2 = st.columns(2)
        
        # Revenue bar chart
        with col_chart1:
            st.markdown("**Revenue per Crop (₹/ha)**")
            chart_revenue_data = pd.DataFrame({
                "Crop": [r.get("crop", "") for r in recommendations],
                "Revenue (₹/ha)": [r.get("expected_revenue_inr_per_ha", 0) for r in recommendations]
            })
            st.bar_chart(
                chart_revenue_data.set_index("Crop"),
                use_container_width=True
            )
        
        # Yield bar chart
        with col_chart2:
            st.markdown("**Yield per Crop (tonnes/ha)**")
            chart_yield_data = pd.DataFrame({
                "Crop": [r.get("crop", "") for r in recommendations],
                "Yield (t/ha)": [r.get("predicted_yield_tonnes_per_ha", 0) for r in recommendations]
            })
            st.bar_chart(
                chart_yield_data.set_index("Crop"),
                use_container_width=True
            )
        
        st.markdown("---")
        
        # ---------------------------------------------------------------------
        # RISK PANEL
        # ---------------------------------------------------------------------
        st.subheader("⚠️ Risk Assessment")
        
        # Get top crop's risk for overall assessment
        top_crop = recommendations[0] if recommendations else {}
        top_risk = top_crop.get("risk_level", "medium").lower()
        top_score = top_crop.get("composite_score", 0.5)
        
        # Calculate average risk score (inverse of composite score)
        avg_score = sum(r.get("composite_score", 0) for r in recommendations) / len(recommendations)
        risk_score = 1 - avg_score  # Higher composite = lower risk
        
        col_risk1, col_risk2, col_risk3 = st.columns(3)
        
        with col_risk1:
            risk_color = get_risk_color(risk_score)
            st.metric(
                label="Overall Risk Score",
                value=f"{risk_score:.2f}",
                delta=get_risk_label(risk_score),
                delta_color="off"
            )
        
        with col_risk2:
            st.metric(
                label="Top Crop Risk",
                value=top_risk.upper(),
                delta=f"Score: {top_score:.3f}"
            )
        
        with col_risk3:
            st.metric(
                label="Avg Composite Score",
                value=f"{avg_score:.3f}",
                delta="Higher is better"
            )
        
        # Risk breakdown by crop
        risk_counts = {"low": 0, "medium": 0, "high": 0}
        for rec in recommendations:
            risk_level = rec.get("risk_level", "medium").lower()
            if risk_level in risk_counts:
                risk_counts[risk_level] += 1
        
        st.markdown(f"""
        **Risk Distribution:**
        - 🟢 Low Risk: {risk_counts['low']} crops
        - 🟠 Medium Risk: {risk_counts['medium']} crops
        - 🔴 High Risk: {risk_counts['high']} crops
        """)
        
    else:
        st.warning("No recommendations returned from the API.")
    
    st.markdown("---")
    
    # -------------------------------------------------------------------------
    # MANDATORY DISCLOSURE BOX
    # -------------------------------------------------------------------------
    st.warning("""
    ⚠️ **Important Disclaimer**
    
    Predictions use **district-level aggregated data** and **model estimates**. 
    This tool is for planning purposes only and is **not a substitute for official agronomic advice**. 
    Consult local agricultural experts before making farming decisions.
    """)
    
    # Display API disclaimer
    api_disclaimer = result.get("disclaimer", "")
    if api_disclaimer:
        st.caption(f"📋 API Note: {api_disclaimer}")

# =============================================================================
# FOOTER
# =============================================================================

st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #888; font-size: 0.9rem;">
        <p>🌾 <strong>KrishiMind SustainAI</strong> — Empowering Indian Farmers with AI</p>
        <p>Hackathon Demo 2026 | District-Level Predictions Only</p>
    </div>
    """,
    unsafe_allow_html=True
)

# =============================================================================
# REQUIREMENTS (as comment)
# =============================================================================
# 
# To run this application:
# 
# 1. Install dependencies:
#    pip install streamlit requests pandas
#
# 2. Ensure the API is running:
#    cd /path/to/agropro
#    uvicorn cloud.api.app:app --host 127.0.0.1 --port 8000
#
# 3. Run the Streamlit app:
#    streamlit run frontend_app.py
#
# Requirements:
#   streamlit>=1.28.0
#   requests>=2.28.0
#   pandas>=1.3.0
#
