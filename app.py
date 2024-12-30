import streamlit as st
import google.generativeai as genai
import os
import av
import speech_recognition as sr
from streamlit_webrtc import WebRtcMode, webrtc_streamer, AudioProcessorBase
from datetime import datetime
from textwrap import dedent
import random
import pandas as pd

# Set up the API key
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', st.secrets.get("GOOGLE_API_KEY"))
if not GOOGLE_API_KEY:
    st.error("Google API Key is missing. Please configure it in your environment or secrets.")
    st.stop()

genai.configure(api_key=GOOGLE_API_KEY)

# Function to transcribe audio using SpeechRecognition
def transcribe_audio_file(audio_file):
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(audio_file) as source:
            audio_data = recognizer.record(source)
            transcription = recognizer.recognize_google(audio_data)
        return transcription
    except Exception as e:
        st.error(f"Error transcribing audio: {e}")
        return "Transcription unavailable."

# Function to generate AI-assisted analysis
def ai_assisted_analysis(text):
    try:
        prompt = dedent(f"""
            Analyze the following patient input and identify:
            1. Emotional tone
            2. Conversation patterns
            3. Any risks (e.g., relapse likelihood, housing insecurity)
            Input: {text}
        """)
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        st.error(f"Error generating analysis: {e}")
        return "Unable to analyze patient input."

# Function to generate personalized insights
def get_personalized_insights():
    try:
        prompt = "Generate a motivational quote for a care provider supporting trauma patients."
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        st.error(f"Error generating insights: {e}")
        return "Keep making a difference!"

# Function to create a downloadable report
def generate_downloadable_report(transcription, analysis):
    report = {
        "Section": ["Transcription", "AI Analysis"],
        "Content": [transcription, analysis]
    }
    df = pd.DataFrame(report)
    csv = df.to_csv(index=False)
    return csv

# Audio Processor for live transcription
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
            recognizer = sr.Recognizer()
            with sr.AudioFile(audio_data) as source:
                audio_content = recognizer.record(source)
                self.transcription = recognizer.recognize_google(audio_content)
        except Exception as e:
            st.error(f"Error transcribing live audio: {e}")
            self.transcription = "Transcription unavailable."
        return self.transcription

# Main app
menu = st.sidebar.selectbox(
    "Navigation", ["Home", "Screening", "Referral", "Follow-Up", "Admin Dashboard"]
)

if menu == "Home":
    st.title("Welcome to Anchor App")
    st.subheader("Dashboard")

    st.write("**Personalized Insights**")
    st.info(get_personalized_insights())

    st.subheader("Quick Access")
    st.markdown("- [Screening Page](#)")
    st.markdown("- [Follow-Up Tasks](#)")
    st.markdown("- [Reports](#)")

    st.subheader("Community Highlights")
    for _ in range(3):
        st.write(f"- {random.choice(['You held space for a patient milestone.', 'You supported a peer through a tough case.', 'You helped celebrate a small but significant victory.'])}")

elif menu == "Screening":
    st.title("Screening Page")

    st.write("**Multimodal Input**")
    text_input = st.text_area("Describe the patient's current situation:")

    st.subheader("Audio Recording")
    audio_processor = AudioProcessor()
    webrtc_streamer(
        key="live_audio",
        mode=WebRtcMode.SENDRECV,
        audio_processor_factory=lambda: audio_processor
    )

    st.subheader("Audio Upload")
    audio_file = st.file_uploader(
        "Upload an audio file (optional):", type=["wav", "mp3"]
    )

    transcription = ""
    if audio_file is not None:
        st.write(f"Uploaded file: {audio_file.name}")
        transcription = transcribe_audio_file(audio_file)
        st.write("**Transcription:**", transcription)

    # Analyze Text or Transcription
    analysis_text = transcription or text_input
    analysis = ""
    if analysis_text.strip():
        analysis = ai_assisted_analysis(analysis_text)
        st.write("**AI-Assisted Analysis:**", analysis)
    else:
        st.warning("Please provide either a text input or an audio file for analysis.")

    # Generate Downloadable Report
    if st.button("Generate Report"):
        if transcription or analysis:
            csv = generate_downloadable_report(transcription, analysis)
            st.download_button(
                label="Download Report",
                data=csv,
                file_name="screening_report.csv",
                mime="text/csv"
            )
        else:
            st.warning("No data available for the report.")

elif menu == "Referral":
    st.title("Referral Page")

    st.subheader("Resource Recommendations")
    st.write("- Local Counseling Center")
    st.write("- Shelter Nearby")

    st.subheader("Referral Tracking")
    st.table({
        "Referral ID": ["R001", "R002"],
        "Status": ["Pending", "Completed"],
        "Date": ["2024-12-05", "2024-12-10"]
    })

elif menu == "Follow-Up":
    st.title("Follow-Up Page")

    st.subheader("Follow-Up Scheduler")
    st.write("- [Dec 15, 2024] Counseling session at 2 PM")
    st.write("- [Dec 20, 2024] Group support meeting at 5 PM")

    st.subheader("Progress Updates")
    update = st.text_area("Enter progress updates:")
    if st.button("Submit Update"):
        st.success("Progress update submitted!")

    st.subheader("HAR Data Insights")
    st.line_chart({"Days": [1, 2, 3, 4], "Activity": [10, 20, 15, 25]})

elif menu == "Admin Dashboard":
    st.title("Admin Dashboard")

    st.subheader("Case Management")
    st.table({
        "Patient ID": ["P001", "P002"],
        "Status": ["In Progress", "Completed"],
        "Last Update": ["2024-12-01", "2024-12-05"]
    })

    st.subheader("Efficiency Metrics")
    st.write("Screening efficiency: 85%")
    st.write("Referral response time: 2 days")

    st.subheader("Guideline Management")
    guideline_file = st.file_uploader("Upload PDF guidelines:", type="pdf")
    if guideline_file:
        st.success("Guidelines uploaded successfully!")

# Footer
st.write("---")
st.write("Powered by Streamlit and Google Gemini")
