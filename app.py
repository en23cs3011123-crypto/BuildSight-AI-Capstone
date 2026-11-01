import base64
import io
import json
from datetime import datetime

import requests
import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="BuildSight AI | Construction Intelligence",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.stApp {background: #0b1118;}
.block-container {max-width: 1450px; padding-top: 1.5rem; padding-bottom: 2.5rem;}
.hero {padding: 1.7rem 1.9rem; border: 1px solid #2d4658; border-radius: 20px;
background: linear-gradient(120deg,#102b3b,#18213a); margin-bottom: 1.2rem;}
.hero h1 {margin:0; font-size:2.3rem; color:#f4f8fb;}
.hero p {color:#b8c9d7; margin:.45rem 0 0 0;}
div[data-testid="stMetric"] {background:#122534; border:1px solid #294354; padding:14px 16px; border-radius:14px;}
div.stButton > button[kind="primary"] {border-radius:10px;}
.note {color:#aab9c7; font-size:.9rem;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <h1>🏗️ BuildSight AI</h1>
  <p>Multimodal Construction Intelligence Platform · Capstone Project</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## Project controls")
    api_key = st.text_input(
        "Gemini API key (optional)",
        type="password",
        help="Used for image interpretation and site Q&A. Leave blank for demo mode.",
    )
    st.caption("The key is kept in this app session. Never commit API keys to GitHub.")
    st.divider()
    st.markdown("### Modules")
    st.markdown("- Site safety & PPE")
    st.markdown("- Crack photo review")
    st.markdown("- Budget & material planning")
    st.markdown("- Weather-aware assistant")
    st.info("No API key? The app still runs with clearly labelled illustrative demo outputs.")

def gemini_generate(prompt, api_key, image=None):
    """Generate a Gemini response; image is optional PIL.Image."""
    parts = [{"text": prompt}]
    if image is not None:
        buffer = io.BytesIO()
        image.convert("RGB").save(buffer, format="JPEG", quality=88)
        parts.append({
            "inline_data": {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(buffer.getvalue()).decode("utf-8"),
            }
        })
    endpoint = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        "gemini-2.0-flash:generateContent"
    )
    response = requests.post(
        endpoint,
        params={"key": api_key},
        headers={"Content-Type": "application/json"},
        json={
            "contents": [{"parts": parts}],
            "generationConfig": {"temperature": 0.2},
        },
        timeout=60,
    )
    response.raise_for_status()
    payload = response.json()
    return payload["candidates"][0]["content"]["parts"][0]["text"]

def image_module(uploaded_file, key, prompt, demo_text, safety_note):
    if uploaded_file is None:
        st.info("Upload a JPG or PNG image to begin.")
        return
    try:
        image = Image.open(uploaded_file)
        image.verify()
        uploaded_file.seek(0)
        image = Image.open(uploaded_file)
    except Exception:
        st.error("That file could not be opened as an image. Please try a JPG or PNG.")
        return

    st.image(image, caption="Uploaded image", use_container_width=True)
    if st.button("Run review", key=f"run_{key}", type="primary"):
        if api_key.strip():
            try:
                with st.spinner("Requesting AI interpretation…"):
                    answer = gemini_generate(prompt, api_key.strip(), image)
                st.session_state[f"{key}_answer"] = answer
                st.session_state[f"{key}_is_demo"] = False
            except Exception as exc:
                st.session_state[f"{key}_answer"] = demo_text
                st.session_state[f"{key}_is_demo"] = True
                st.session_state[f"{key}_error"] = type(exc).__name__
        else:
            st.session_state[f"{key}_answer"] = demo_text
            st.session_state[f"{key}_is_demo"] = True

    answer_key = f"{key}_answer"
    if answer_key in st.session_state:
        if st.session_state.get(f"{key}_is_demo", True):
            st.warning("DEMO OUTPUT — this is an illustrative checklist, not analysis of the image.")
            if f"{key}_error" in st.session_state:
                st.caption(f"AI request failed ({st.session_state[f'{key}_error']}).")
        else:
            st.success("AI-generated interpretation — independently verify all findings.")
        st.markdown(st.session_state[answer_key])
        st.download_button(
            "Download report (.txt)",
            data=st.session_state[answer_key],
            file_name=f"{key}_report.txt",
            mime="text/plain",
            key=f"download_{key}",
        )
    st.caption(safety_note)

tabs = st.tabs([
    "🦺 Safety & PPE",
    "🧱 Crack Review",
    "📐 Cost Planning",
    "🌦️ Site Assistant",
])

with tabs[0]:
    st.subheader("Site Safety & PPE Audit")
    st.write("Review visible safety conditions and build a checklist for a supervisor to verify.")
    upload = st.file_uploader("Construction-site photo", type=["jpg", "jpeg", "png"], key="ppe_upload")
    prompt = (
        "Review this construction site photo cautiously. Identify only visible observations and "
        "uncertainties. Return sections: Visible observations; PPE checklist (hard hats, high-visibility "
        "clothing, eye protection, footwear, fall protection where relevant); potential hazards with "
        "priority; corrective actions. Do not infer unseen details or certify legal compliance."
    )
    demo = """
### Example safety checklist (demo mode)
- **Hard hats:** Verify visually for every worker in designated areas.
- **High-visibility clothing:** Check that workers are visible to equipment operators.
- **Work at height:** Check guardrails, approved fall-protection systems and anchor points.
- **Housekeeping:** Keep walkways clear and materials stacked securely.
- **Electrical safety:** Check temporary wiring, connections and water exposure.

**Next step:** Have the site supervisor complete and document a site-specific inspection.
"""
    image_module(
        upload, "ppe", prompt, demo,
        "A photo review cannot certify compliance. Follow local regulations and the approved site safety plan.",
    )

with tabs[1]:
    st.subheader("Crack Diagnostics & Defect Review")
    st.write("Record visible defects and determine when a qualified professional should assess them.")
    upload = st.file_uploader("Wall or concrete photo", type=["jpg", "jpeg", "png"], key="crack_upload")
    prompt = (
        "Describe only what is visible in this wall/concrete photo. Include visible pattern, limitations "
        "from lighting/scale, possible causes as non-diagnostic possibilities, recommended measurements "
        "and documentation, and reasons to contact a licensed structural engineer. Do not estimate width "
        "without a visible scale. Never declare the structure safe based on a photo."
    )
    demo = """
### Defect documentation checklist (demo mode)
- **Image assessment:** Demo mode does not analyze image pixels.
- **Record:** Photograph with a scale, note location, length, direction and whether the crack changes.
- **Possible causes:** Shrinkage, temperature movement, settlement or structural movement; a photo cannot distinguish these reliably.
- **Escalate:** Ask a licensed structural engineer about widening cracks, displacement, exposed reinforcement, water ingress or other concerning changes.
- **Precaution:** If instability is suspected, keep people away from the affected area and contact the responsible site professional.

**No severity score or safety determination is provided in demo mode.**
"""
    image_module(
        upload, "crack", prompt, demo,
        "Do not use this module to approve occupancy, repairs or structural safety.",
    )

with tabs[2]:
    st.subheader("Construction Planning & Indicative Valuation")
    st.caption("All rates are editable assumptions for a classroom prototype, not market quotations.")
    c1, c2, c3 = st.columns(3)
    with c1:
        structure = st.selectbox("Structure type", ["Residential", "Commercial", "Industrial"])
        area = st.number_input("Built-up area (sq ft)", min_value=100, max_value=1_000_000, value=2500, step=100)
    with c2:
        tier = st.selectbox("Location tier", ["Tier 1", "Tier 2", "Tier 3"])
        completion = st.slider("Completion (%)", 0, 100, 35)
    with c3:
        default_rate = {"Residential": 2200, "Commercial": 3000, "Industrial": 1800}[structure]
        rate = st.number_input("Construction rate (₹/sq ft)", min_value=500, max_value=20000, value=default_rate, step=100)
        default_market = {"Tier 1": 6500, "Tier 2": 4200, "Tier 3": 2800}[tier]
        market_rate = st.number_input("Indicative market rate (₹/sq ft)", min_value=500, max_value=50000, value=default_market, step=100)

    total = area * rate
    incurred = total * completion / 100
    market = area * market_rate
    contingency = total * 0.10
    steel_factor = {"Residential": 4.0, "Commercial": 5.0, "Industrial": 6.0}[structure]
    cement_factor = {"Residential": 0.40, "Commercial": 0.45, "Industrial": 0.35}[structure]
    steel_kg = area * steel_factor
    cement_bags = area * cement_factor

    st.markdown("#### Estimate summary")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Estimated budget", f"₹{total / 100000:.2f} lakh")
    m2.metric("Progress-based spend", f"₹{incurred / 100000:.2f} lakh")
    m3.metric("Indicative market value", f"₹{market / 100000:.2f} lakh")
    m4.metric("10% contingency", f"₹{contingency / 100000:.2f} lakh")
    st.progress(completion / 100, text=f"Milestone progress: {completion}%")

    st.markdown("#### Rough material-planning assumptions")
    a, b = st.columns(2)
    a.metric("Indicative steel", f"{steel_kg:,.0f} kg")
    b.metric("Indicative cement", f"{cement_bags:,.0f} bags")

    report = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "disclaimer": "Illustrative estimate only; not a BOQ, quotation, appraisal or engineering design.",
        "structure_type": structure,
        "area_sqft": area,
        "location_tier": tier,
        "completion_percent": completion,
        "construction_rate_inr_per_sqft": rate,
        "estimated_total_budget_inr": round(total),
        "estimated_incurred_inr": round(incurred),
        "indicative_market_value_inr": round(market),
        "contingency_10_percent_inr": round(contingency),
        "indicative_steel_kg": round(steel_kg),
        "indicative_cement_bags": round(cement_bags),
    }
    st.download_button(
        "Download estimate (JSON)",
        data=json.dumps(report, indent=2),
        file_name="construction_estimate.json",
        mime="application/json",
    )

with tabs[3]:
    st.subheader("Weather-Aware Site Assistant")
    weather = st.selectbox("Current site condition", ["Normal", "High Wind", "Heavy Rain", "Extreme Heat"])
    advice = {
        "Normal": ("Routine controls", [
            "Run a toolbox talk and daily risk assessment.",
            "Inspect access routes, PPE and lifting equipment.",
            "Keep emergency access and first-aid supplies clear.",
        ]),
        "High Wind": ("Review lifting and work-at-height activities", [
            "Follow manufacturer wind limits and the approved lifting plan.",
            "Pause work when equipment limits or site rules require it.",
            "Secure loose materials and reassess elevated work.",
        ]),
        "Heavy Rain": ("Water, slips and electrical hazards", [
            "Inspect drainage and avoid unsafe flooded areas.",
            "Have electrical equipment exposed to water isolated and checked by qualified personnel.",
            "Review excavation stability and task-specific weather restrictions.",
        ]),
        "Extreme Heat": ("Heat-stress prevention", [
            "Provide drinking water, shade and appropriate rest breaks.",
            "Use a buddy system and watch for signs of heat illness.",
            "Adjust work/rest schedules under applicable occupational safety guidance.",
        ]),
    }
    heading, items = advice[weather]
    st.warning(heading)
    for item in items:
        st.markdown(f"- {item}")

    st.markdown("#### Ask a general site question")
    question = st.text_input("Question", placeholder="What should we check before a concrete pour?")
    if st.button("Get guidance", type="primary", key="site_question"):
        if not question.strip():
            st.info("Enter a question first.")
        elif api_key.strip():
            try:
                answer = gemini_generate(
                    "You are a cautious construction site information assistant. Provide a general checklist, "
                    "state assumptions, and never certify structural safety or replace local codes, the site "
                    "safety plan, or qualified professionals. Weather condition: " + weather +
                    ". User question: " + question,
                    api_key.strip(),
                )
                st.markdown(answer)
            except Exception:
                st.warning("AI service unavailable. Use the checklist above and consult the site supervisor.")
        else:
            st.info(
                "Demo guidance: document the task, identify hazards, confirm PPE and permits, check "
                "equipment and weather constraints, and ask the site supervisor to approve the task method."
            )

st.divider()
st.markdown(
    '<p class="note">BuildSight AI · Educational capstone prototype · Verify all construction, safety, '
    'cost and structural decisions with qualified professionals.</p>',
    unsafe_allow_html=True,
)
