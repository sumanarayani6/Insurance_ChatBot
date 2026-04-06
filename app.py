import streamlit as st
from google import genai
import traceback
import os
from dotenv import load_dotenv

# 1. Setup
load_dotenv()

# Fetch the key securely
API_KEY = os.getenv("GEMINI_API_KEY")

# Safety check for API Key
if not API_KEY:
    st.error("API Key not found! Please check your .env file.")
    st.stop()

client = genai.Client(api_key=API_KEY)

st.set_page_config(page_title="Insurance AI Assistant", page_icon="🛡️")

# 2. INITIALIZE SESSION STATE
if "messages" not in st.session_state:
    st.session_state.messages = []

# 3. UI LAYOUT
st.title("🛡️ Insurance AI Assistant")
st.markdown("*Your expert guide to life, health, auto, and home protection.*")

# 4. DISPLAY LOOP
for message in st.session_state.messages:
    display_role = "assistant" if message["role"] == "model" else "user"
    with st.chat_message(display_role):
        st.markdown(message["parts"][0]["text"])

# 5. GENERAL INSURANCE PERSONA
# This is where we change the 'brain' of the bot
GENERAL_SYSTEM_INSTRUCTION = (
    "You are a knowledgeable and friendly General Insurance Assistant. "
    "Your goal is to explain complex insurance concepts (deductibles, premiums, "
    "coverage limits, etc.) in simple terms. You can provide information on "
    "Life, Health, Auto, Home, and Pet insurance. Be supportive and professional. "
    "If you don't know a specific state-level regulation, suggest the user consult "
    "a licensed agent in their area. Remind the user they can type 'exit' or 'quit' to stop."
)

# 6. CHAT LOGIC
if prompt := st.chat_input("Ask me anything about insurance..."):
    
    if prompt.lower() in ["exit", "quit"]:
        st.info("Thank you for using the Insurance Assistant. Stay protected!")
        st.stop()

    # Show and save user message
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "parts": [{"text": prompt}]})

    # Generate response
    with st.chat_message("assistant"):
        try:
            # We pass the last 6 messages for context
            response = client.models.generate_content(
                model="gemini-3-flash-preview", 
                config={'system_instruction': GENERAL_SYSTEM_INSTRUCTION},
                contents=st.session_state.messages[-6:]
            )
            
            st.markdown(response.text)
            st.session_state.messages.append({"role": "model", "parts": [{"text": response.text}]})

        except Exception as e:
            stack_trace = traceback.format_exc()
            st.error("⚠️ An error occurred while generating the response.")
            with st.expander("🔍 Debug Call Stack"):
                st.code(stack_trace, language="python")