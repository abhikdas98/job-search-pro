from config.configfile import config
from langchain_groq import ChatGroq
from app.ui.streamlit.load_ui import LoadStreamlitUI

ui = LoadStreamlitUI()
user_input = ui.load_streamlit_ui()

config = config()

llm = ChatGroq(
    model=user_input.user_controls["selected_groq_model"],
    api_key=config
               )