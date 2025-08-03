
import streamlit as st
import time

# Apply Carson-based color theme
st.markdown("""
    <style>
    body, .main {
        background-color: #001E62; /* Carson High navy blue */
        color: #f0f6fc;
        font-family: 'Segoe UI', sans-serif;
    }
    .emotion-box {
        background-color: #00388b;
        padding: 1rem;
        border-radius: 0.75rem;
        margin-bottom: 1rem;
        border-left: 5px solid #FFD700; /* Carson yellow/gold */
    }
    .stButton>button {
        background-color: #FFD700 !important;
        color: black;
        font-weight: bold;
    }
    .stTextInput>div>input, .stTextArea>div>textarea {
        background-color: #e6f0ff;
        color: #001E62;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.title("🎓 CGP: Carson-Branded Plan Matcher")
st.caption("📍 Built with the pride of Carson High — Purpose-driven, soul-matched care")

# Input form
with st.form("match_form"):
    artist = st.text_input("🎧 Your Artist", "Ab-Soul")
    vibe = st.text_input("🌱 Desired Plan Vibe", "Low bureaucracy, high value")
    quote = st.text_area("🗣️ Describe Your Ideal Experience", "I found this plan that'll cure the loneliness for you. It'll help connect you with people in the community.")
    submitted = st.form_submit_button("🔎 Match My Plan")

# Processing and output
if submitted:
    with st.spinner("Tuning into your emotional frequency..."):
        time.sleep(2)

    st.markdown("## 🎧 Your Emotional Fingerprint")
    st.markdown(f"<div class='emotion-box'>🎤 <b>Artist:</b> {artist}<br>🎯 <b>Vibe:</b> {vibe}<br>🗣️ <b>Quote:</b> {quote}</div>", unsafe_allow_html=True)

    st.markdown("## 🧠 Inferred Traits")
    st.markdown("""
        <div class='emotion-box'>
        - Deeply introspective<br>
        - Distrusts red tape<br>
        - Craves self-guided autonomy<br>
        - Seeks connection only when it feels real<br>
        - Needs systems that don’t talk down to them
        </div>
    """, unsafe_allow_html=True)

    st.markdown("## 🩺 Plan Match: UnityCare Connect Lite+")
    st.progress(87)
    st.markdown("""
        <div class='emotion-box'>
        ✅ Minimal forms<br>
        ✅ Auto-assigned local concierge<br>
        ✅ Built-in community events & transportation<br>
        ✅ No pre-auth needed for specialists<br>
        ✅ Emotional support via app or in-person<br>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("## 🧪 Bias & Validation Check")
    st.warning("⚠️ Potential misread: Plan assumes you want community engagement when you may need autonomy.")
    st.markdown("""
        <div class='emotion-box'>
        🔁 Reframe it: "Freedom-first coverage — support if you want it, solitude if you need it."
        </div>
    """, unsafe_allow_html=True)

    st.markdown("## ✅ Final Recommendation")
    st.success("This plan helps you stay in control without paperwork hell. It quietly keeps the door open to connection—but only if you want it. No pressure. No fluff. Just care that listens.")

    st.caption("Confidence Score: 8.7/10 | Branded by Carson Engine | Powered by CGP")
