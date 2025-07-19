import streamlit as st
import time
from langgraph_logic import build_graph
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set your Gemini API key
if not os.getenv("GOOGLE_API_KEY"):
    if "GOOGLE_API_KEY" in st.secrets:
        os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
    else:
        api_key = st.text_input("Enter your Gemini API key:", type="password")
        if api_key:
            os.environ["GOOGLE_API_KEY"] = api_key

# Initialize the LangGraph only if API key is set
if os.getenv("GOOGLE_API_KEY"):
    graph = build_graph()
else:
    st.error("Please set your Google API key to continue")
    st.stop()

# Simulated ward storage (in-memory)
if "wards" not in st.session_state:
    st.session_state.wards = {
        "general": [],
        "mental health": [],
        "emergency": []
    }

# App Layout
st.title("🏥 Green Valley Hospital - Symptom Classifier & Ward Routing")

tab1, tab2 = st.tabs(["🧑‍⚕ Patient Intake", "📋 Admin Dashboard"])

# -----------------------------
# 🧑‍⚕ Patient Intake Tab
# -----------------------------
with tab1:
    st.subheader("Describe Your Symptoms")

    name = st.text_input("Patient Name")
    symptom = st.text_area("Enter your symptom")

    if st.button("Submit Symptom"):
        if not name or not symptom:
            st.warning("Please enter both name and symptom.")
        else:
            state = {
                "user_input": symptom,
                "name": name,
                "time": time.strftime("%Y-%m-%d %H:%M:%S")
            }

            result = graph.invoke(state)
            category = result["category"].lower()
            answer = result["answer"]

            # Save to ward
            patient_data = {
                "name": name,
                "symptom": symptom,
                "time": state["time"]
            }
            st.session_state.wards[category].append(patient_data)

            st.success(answer)

# -----------------------------
# 📋 Admin Dashboard Tab
# -----------------------------
with tab2:
    st.subheader("Ward Overview")

    for ward in ["general", "mental health", "emergency"]:
        with st.expander(f"🛏 {ward.title()} Ward"):
            patients = st.session_state.wards[ward]
            if not patients:
                st.info("No patients in this ward.")
            else:
                for i, p in enumerate(patients, 1):
                    st.markdown(f"{i}. Name:** {p['name']}  \n"
                                f"🕒 *Time:* {p['time']}  \n"
                                f"🩺 *Symptom:* {p['symptom']}")
                    st.divider()