import whisper
import sounddevice as sd
import numpy as np

class WhisperListener:
    def __init__(self, model_size="base"):
        print("Loading Whisper model...")
        self.model = whisper.load_model(model_size)  # Load the model (options: tiny, base, small, medium, large)
        self.sampling_rate = 16000  # Whisper works best with 16kHz audio

    def record_audio(self, duration=5):
        """Records audio from the microphone for a given duration."""
        print("Recording...")
        audio = sd.rec(int(duration * self.sampling_rate), samplerate=self.sampling_rate, channels=1, dtype=np.float32)
        sd.wait()  # Wait for recording to complete
        print("Recording complete.")
        return audio.flatten()

    def transcribe_audio(self, audio):
        """Transcribes the recorded audio using Whisper."""
        print("Transcribing...")
        transcription = self.model.transcribe(audio)
        return transcription["text"]

    def start_listening(self, duration=5):
        """Record and transcribe speech in a loop."""
        while True:
            try:
                audio = self.record_audio(duration)
                text = self.transcribe_audio(audio)
                print(f"Transcription: {text}")
            except KeyboardInterrupt:
                print("\nStopping listener.")
                break

# # Usage Example:
# listener = WhisperListener(model_size="tiny")  # Load the "base" model
# listener.start_listening(duration=10)  # Record & transcribe every 5 seconds
