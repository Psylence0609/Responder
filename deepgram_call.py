import os
from deepgram import DeepgramClient, SpeakOptions
from dotenv import load_dotenv 
import re  
load_dotenv()

def segmentTextBySentence(text):
    return re.findall(r"[^.!?]+[.!?]", text)

def synthesize_audio(prompt, filename):
    # Load credentials from .env file
    try:
        DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
        SPEAK_OPTIONS = {"text": prompt}
        deepgram = DeepgramClient(DEEPGRAM_API_KEY)
        options = SpeakOptions(
            model="aura-asteria-en",
        )
        response = deepgram.speak.rest.v("1").save(filename, SPEAK_OPTIONS, options)
        # print(response.to_json(indent=4))
        return response
    except Exception as e:
        print(e)
    
