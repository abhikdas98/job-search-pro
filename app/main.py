import streamlit as st

from app.ui.streamlit.load_ui import LoadStreamlitUI

def load_agenticai_app():
    """
    Loads and runs the LangGraph Agentic AI Application with Streamlist UI.
    This functoin initializes the UI, handles user input, loads LLM model,
    sets up the graph based on the selected use case, and displays the output
    while handling the exceptions for robustness.
    """
    ui = LoadStreamlitUI()
    user_input = ui.load_streamlit_ui()

    if not user_input:
        st.error("Error: Failed to load user input from the UI")

    user_message = st.chat_input("Enter your message:")

    