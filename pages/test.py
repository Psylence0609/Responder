import streamlit as st
from assistant import FirstResponderAssistant

st.title("Patient Intake Assistant")

assistant = FirstResponderAssistant()
assistant.start_assistance_flow()