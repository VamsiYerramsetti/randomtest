# frontend/app.py
import os
import requests
import streamlit as st

st.set_page_config(page_title="Azure OpenAI Chatbot", page_icon="💬", layout="centered")
st.title("💬 Azure OpenAI Chatbot (GPT‑4o‑mini)")

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")  # will point to internal URL in Azure

user_input = st.text_input("Ask me anything:", "")
if st.button("Ask") and user_input.strip():
    with st.spinner("Thinking..."):
        try:
            r = requests.post(f"{BACKEND_URL}/chat", json={"message": user_input}, timeout=60)
            r.raise_for_status()
            st.success(r.json().get("answer", "No answer returned."))
        except Exception as e:
            st.error(f"Error: {e}")