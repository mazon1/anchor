import streamlit as st
from datetime import datetime
import random
from streamlit_webrtc import webrtc_streamer

# Page configuration
st.set_page_config(page_title="Anchor App", layout="wide")

# Synthetic Data Generators
def generate_story():
    emotions = ["hopeful", "anxious", "grateful", "struggling"]
    events = [
        "held a space for a patient's recovery milestone",
        "collaborated with peers to solve a challenging case",
        "provided emotional support during a difficult session",
        "celebrated a patient's small but significant victory",
    ]
    return f"Today, feeling {random.choice(emotions)}, you {random.choice(events)}."

# Sidebar Navigation
menu = st.sidebar.selectbox("Navigation", ["Home", "Screening", "Referral", "Follow-Up", "Admin Dashboard"])

if menu == "Home":
    st.title("Welcome to Anchor")
    st.subheader("Your Dashboard")

    st.write("**Personalized Insights**")
    st.info(random.choice([
        "You are making a difference one step at a time.",
        "Your work is vital to our community.",
        "Small acts of kindness have a big impact."
    ]))

    st.subheader("Community Highlights")
    for _ in range(3):
        st.write(f"- {generate_story()}")

elif menu == "Screening":
    st.title("Screening Page")

    st.write("Use multimodal inputs to gather insights.")
    text_input = st.text_area("Describe the patient's current situation:")
    st.subheader("Audio Recording")
    audio_data = webrtc_streamer(key="audio")

    image_file = st.file_uploader("Upload an image (optional):", type=["jpg", "png"])
    
    if st.button("Submit Screening Data"):
        st.success("Screening data submitted successfully!")

elif menu == "Referral":
    st.title("Referral Page")

    st.write("Provide personalized recommendations and manage referrals.")
    st.subheader("Resource Recommendations")
    st.write("- Local Counseling Center")
    st.write("- Shelter Nearby")

    st.subheader("Track Referrals")
    st.table({
        "Referral ID": ["R001", "R002"],
        "Status": ["Pending", "Completed"],
        "Date": ["2024-12-05", "2024-12-10"]
    })

elif menu == "Follow-Up":
    st.title("Follow-Up Page")

    st.subheader("Follow-Up Calendar")
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

    st.subheader("Upload Guidelines")
    guideline_file = st.file_uploader("Upload PDF guidelines:", type="pdf")
    if guideline_file:
        st.success("Guidelines uploaded successfully!")

# Footer
st.write("---")
st.write("Powered by Streamlit")
