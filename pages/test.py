import streamlit as st
from assistant import FirstResponderAssistant

st.title("Let me see if I remember you... This may take some time")

assistant = FirstResponderAssistant()
assistant.start_assistance_flow()