import os
import streamlit as st
from datetime import datetime
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase
import av
import random
import requests

# Define API Key and Gemini API Endpoint
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', st.secrets["GOOGLE_API_KEY"])
GEMINI_API_ENDPOINT = "https://gemini-api.google.com/v2"
HEADERS = {
    "Authorization": f"Bearer {GOOGLE_API_KEY}",
    "Content-Type": "application/json"
}

# Page Configuration
st.set_page_config(page_title="Anchor App", layout="wide")

# Generate Personalized Insights
@st.cache_data
def get_motivational_quote():
    try:
        response = requests.post(
            GEMINI_API_ENDPOINT + "/generate-text",
            headers=HEADERS,
            json={"prompt": "Generate a motivational quote for a care provider."}
        )
        response.raise_for_status()
        return response.json().get("text", "Keep making a difference!")
    except requests.exceptions.RequestException as e:
        st.error(f"API error: {e}")
        return "Unable to fetch motivational quote at this time."

# Audio Processor for Live Transcription
class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.audio_queue = []
        self.transcription = ""

    def recv_audio(self, frame: av.AudioFrame):
        audio_bytes = frame.to_ndarray().tobytes()
        self.audio_queue.append(audio_bytes)
        return frame

    def transcribe_audio(self):
        try:
            audio_data = b"".join(self.audio_queue)
            self.audio_queue.clear()
            response = requests.post(
                GEMINI_API_ENDPOINT + "/transcribe-audio",
                headers=HEADERS,
                files={"audio": ("audio.wav", audio_data, "audio/wav")}
            )
            response.raise_for_status()
            self.transcription = response.json().get("transcription", "Transcription unavailable.")
        except requests.exceptions.RequestException as e:
            st.error(f"Transcription API error: {e}")
            self.transcription = "Transcription unavailable."
        return self.transcription

# Core Pages
menu = st.sidebar.selectbox(
    "Navigation", ["Home", "Screening", "Referral", "Follow-Up", "Admin Dashboard"]
)

if menu == "Home":
    st.title("Welcome to Anchor")
    st.subheader("Your Dashboard")

    st.write("**Personalized Insights**")
    st.info(get_motivational_quote())

    st.subheader("Community Highlights")
    for _ in range(3):
        st.write(f"- Today, feeling {random.choice(['hopeful', 'anxious', 'grateful'])}, you {random.choice(['supported a patient', 'collaborated with peers', 'celebrated a small victory'])}.")

elif menu == "Screening":
    st.title("Screening Page")

    st.write("Use multimodal inputs for comprehensive screening.")
    text_input = st.text_area("Describe the patient's current situation:")

    st.subheader("Audio Recording")
    audio_processor = AudioProcessor()
    webrtc_streamer(key="audio", mode="sendrecv", audio_processor_factory=lambda: audio_processor)

    st.subheader("Image Upload")
    image_file = st.file_uploader("Upload an image (optional):", type=["jpg", "png"])

    if st.button("Submit Screening Data"):
        transcription = audio_processor.transcribe_audio()
        st.write("**Transcription:**", transcription)

        response = requests.post(
            GEMINI_API_ENDPOINT + "/analyze-text",
            headers=HEADERS,
            json={"text": transcription}
        )
        analysis = response.json().get("analysis", "No analysis available.")
        st.write("**AI Analysis:**", analysis)

# (Other pages remain the same)

st.write("---")
st.write("Powered by Streamlit and Google Gemini")
