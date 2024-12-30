import streamlit as st
import google.generativeai as genai
import os
import av
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase
from datetime import datetime
from textwrap import dedent
import random

# Set up the API key
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', st.secrets.get("GOOGLE_API_KEY"))
if not GOOGLE_API_KEY:
    st.error("Google API Key is missing. Please configure it in your environment or secrets.")
    st.stop()

genai.configure(api_key=GOOGLE_API_KEY)

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
            prompt = "Transcribe this audio data."
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt, audio=audio_data)
            self.transcription = response.text.strip()
        except Exception as e:
            st.error(f"Error transcribing audio: {e}")
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
    webrtc_streamer(key="audio", mode="sendrecv", audio_processor_factory=lambda: audio_processor)

    st.subheader("Image Upload")
    image_file = st.file_uploader("Upload an image (optional):", type=["jpg", "png"])

    if st.button("Submit Screening Data"):
        transcription = audio_processor.transcribe_audio()
        st.write("**Transcription:**", transcription)

        analysis = ai_assisted_analysis(transcription or text_input)
        st.write("**AI-Assisted Analysis:**", analysis)

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
