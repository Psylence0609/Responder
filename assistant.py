import os
import time
from typing import Optional
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage, AIMessage
from langchain.memory import ConversationBufferWindowMemory
from deepgram_call import synthesize_audio
from Listener import WhisperListener
from face_recog import FaceIdentifier
import sounddevice as sd
import soundfile as sf
import numpy as np
import cv2


class FirstResponderAssistant:
    def __init__(self):
        # Initialize components
        self.face_identifier = FaceIdentifier()
        self.listener = WhisperListener(model_size="base")
        self.llm = self._setup_llm()
        self.memory = ConversationBufferWindowMemory(k=5)
        self.current_patient: Optional[str] = None
        
        # Audio settings
        self.sampling_rate = 16000
        self.audio_duration = 5  # seconds
        
        # Initialize prompts
        self.system_prompt = """You are a professional first responder assisting in an emergency situation. 
        Your responses should be calm, clear, and focused on gathering critical information. 
        Ask one question at a time. 
        Prioritize assessing:
        - The patient's symptoms
        Keep responses brief and to the point.
        Important Points to remember:
        1. Refer to the previous questions asked. DO NOT ask the same question again .
        2. Ask questions based on the patient's response.
        3. If you do not understand the patient's response, ask them to repeat or clarify.
        4. IF you feel that you have asked enough questions end the conversation by respoining with "Thank you for your time. I will now hand you over to the required person." """
        
        self.prompt_template = PromptTemplate(
            input_variables=["history", "input", "patient_name"],
            template=self.system_prompt + """
            Current conversation:
            {history}
            Patient: {input}
            Important: You have only {question_count} questions left to ask. Please ask relevant ones to gather maximum information within the limit.
            Responder:"""
        )

    def _setup_llm(self):
        return ChatGroq(
            temperature=0.3,
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name="llama-3.3-70b-versatile"
        )
    
    def delete_file(file_path):
        if os.path.exists(file_path):
            os.remove(file_path)
            
    def _play_audio(self, filename):
        """Play generated audio response"""
        try:
            data, fs = sf.read(filename)
            sd.play(data, fs)
            sd.wait()
        except Exception as e:
            print(f"Error playing audio: {e}")

    def _get_llm_response(self, user_input: str, question_count: int) -> str:
        """Get response from LLM with conversation history"""
        # Format conversation history
        history = self.memory.load_memory_variables({})["history"]
        
        # Format prompt
        formatted_prompt = self.prompt_template.format(
            history=history,
            input=user_input,
            patient_name=self.current_patient or "Patient",
            question_count=question_count
        )
        
        # Get response
        response = self.llm.invoke(formatted_prompt)
        return response.content

    def start_assistance_flow(self):
        """Main loop for first responder assistance"""
        print("Starting first responder assistant...")
        
        # Start face recognition
        
        try:
            self.current_patient = self.face_identifier.run_recognition()
            print(f"Detected patient: {self.current_patient}")
            # Start conversation loop
            print("Starting conversation...")
            response = self._get_llm_response("First responder has arrived. How can I help you?", question_count=13)
            print(f"Responder: {response}")
            question_count = 13
            while question_count:
                # Generate and play audio
                audio_file = f"response_{int(time.time())}.wav"
                synthesize_audio(response, audio_file)
                self._play_audio(audio_file)

                if "Thank you for your time" in response:
                    break
                # Listen for patient response
                print("Listening...")
                audio = self.listener.record_audio(self.audio_duration)
                user_input = self.listener.transcribe_audio(audio)
                print(f"Patient: {user_input}")
                if question_count == 1:
                    response += " Thank you for your time. I will now hand you over to the required person."
                    audio_file = f"response_{int(time.time())}.wav"
                    synthesize_audio(response, audio_file)
                    self._play_audio(audio_file)
                    break
                if "quit" in user_input.lower():
                    break
                
                # Get and store response
                self.memory.save_context(
                    {"input": user_input},
                    {"output": response}
                )
                response = self._get_llm_response(user_input, question_count)
                print(f"Responder: {response}")
                question_count-=1
                
        finally:
            cv2.destroyAllWindows()