import streamlit as st
from audio_recorder_streamlit import audio_recorder
import os
import google.generativeai as genai
from dotenv import load_dotenv
from textwrap import dedent
import pandas as pd
import tempfile
from pydub import AudioSegment

# Initialize Google Gemini API
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    st.error("Google API Key is missing. Please configure it in your environment or secrets.")
    st.stop()

genai.configure(api_key=GOOGLE_API_KEY)

# Function to preprocess audio with PyDub and convert to WAV
def preprocess_audio(audio_bytes):
    try:
        temp_audio_path = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
        audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format="mp3")
        audio.export(temp_audio_path, format="wav")
        return temp_audio_path
    except Exception as e:
        st.error(f"Error processing audio file: {e}")
        return None

# Function to transcribe audio using Google Gemini
def transcribe_audio_with_gemini(audio_file_path):
    try:
        with open(audio_file_path, "rb") as audio_file:
            prompt = dedent("""
                Please transcribe the following audio file and return the text transcription:
            """)
            model = genai.GenerativeModel("gemini-pro")
            response = model.generate_content(prompt)
            return response.text.strip()
    except Exception as e:
        st.error(f"Error transcribing audio: {e}")
        return "Transcription unavailable."

# Function to generate AI-assisted analysis
def ai_assisted_analysis(text):
    try:
        prompt = dedent(f"""
            Analyze the following text and identify:
            1. Emotional tone
            2. Conversation patterns
            3. Any risks (e.g., relapse likelihood, housing insecurity)
            Input: {text}
        """)
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        st.error(f"Error generating analysis: {e}")
        return "Unable to analyze text."

# Function to create a downloadable report
def generate_downloadable_report(transcription, analysis):
    report = {
        "Section": ["Transcription", "AI Analysis"],
        "Content": [transcription, analysis]
    }
    df = pd.DataFrame(report)
    return df.to_csv(index=False)

# Streamlit app
st.title("Audio Transcription and Chat with Gemini")
st.write("Record, upload, or analyze audio using Google Gemini.")

# Audio Recorder
st.subheader("Audio Recording")
audio_bytes = audio_recorder()
audio_file_path = None
if audio_bytes:
    audio_file_path = preprocess_audio(audio_bytes)
    if audio_file_path:
        st.audio(audio_bytes, format="audio/wav")
        st.success("Audio recorded successfully!")

# File Upload
st.subheader("Upload Audio File")
uploaded_file = st.file_uploader("Choose an audio file", type=["wav", "mp3"])
if uploaded_file:
    temp_audio_path = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
    audio = AudioSegment.from_file(uploaded_file, format="mp3")
    audio.export(temp_audio_path, format="wav")
    audio_file_path = temp_audio_path
    st.audio(uploaded_file, format="audio/wav")
    st.success("File uploaded successfully!")

# Transcription and Analysis
if audio_file_path:
    if st.button("Transcribe and Analyze"):
        transcription = transcribe_audio_with_gemini(audio_file_path)
        st.write("**Transcription:**", transcription)

        if transcription:
            analysis = ai_assisted_analysis(transcription)
            st.write("**AI-Assisted Analysis:**", analysis)

            # Generate downloadable report
            report_csv = generate_downloadable_report(transcription, analysis)
            st.download_button(
                label="Download Report",
                data=report_csv,
                file_name="transcription_analysis_report.csv",
                mime="text/csv"
            )
