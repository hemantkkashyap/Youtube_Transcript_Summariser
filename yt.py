import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound

# Load environment variables
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    st.error("API key not found. Please set the GOOGLE_API_KEY in your environment variables.")
else:
    genai.configure(api_key=API_KEY)

# Default prompt for Google Gemini Pro
base_prompt = """
You are an expert summarizer for YouTube videos. Your task is to create a clear and insightful summary based on the transcript. Include:

1. **Key Points**: Main ideas discussed.
2. **Conclusions**: Important takeaways or recommendations.
3. **Insights**: Notable facts, figures, or unique ideas shared.

Here is the transcript to summarize:
"""

# Function to get the transcript data from YouTube videos
def extract_transcript(youtube_video_url):
    try:
        # Extract video ID from various YouTube URL formats
        if "youtu.be" in youtube_video_url:
            video_id = youtube_video_url.split("/")[-1]
        elif "v=" in youtube_video_url:
            video_id = youtube_video_url.split("v=")[1].split("&")[0]
        else:
            st.error("Invalid YouTube link. Please enter a valid link.")
            return None, None

        # Try to retrieve the English transcript first
        try:
            transcript_data = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        except NoTranscriptFound:
            transcript_data = YouTubeTranscriptApi.get_transcript(video_id, languages=['hi'])

        transcript = " ".join([item["text"] for item in transcript_data])
        return transcript, video_id
    except Exception as e:
        st.error(f"Error fetching transcript: {str(e)}. Please check the video URL or try another video.")
        return None, None

# Function to generate a summary using Google Gemini Pro
def generate_summary(transcript_text, prompt):
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt + transcript_text)
        return response.text.strip()
    except Exception as e:
        st.error("Error generating summary. Please try again.")
        return None

# Streamlit App UI
st.title("YouTube Video Summarizer")
youtube_link = st.text_input("Enter YouTube Video Link:")

# Sidebar options for customization
st.sidebar.header("Summary Settings")
summary_length = st.sidebar.slider("Max Words for Summary", min_value=50, max_value=5000, value=250, step=50)
summary_format = st.sidebar.radio("Summary Format", options=["Bullet Points", "Paragraph"])

# Configure prompt based on settings
prompt = base_prompt
if summary_format == "Bullet Points":
    prompt += f" Summarize in bullet points, keeping within {summary_length} words."
elif summary_format == "Paragraph":
    prompt += f" Provide a single coherent paragraph, strictly avoiding bullet points and within {summary_length} words."

# Button to fetch and display the summary
if st.button("Generate Summary"):
    with st.spinner("Extracting transcript and generating summary..."):
        transcript_text, video_id = extract_transcript(youtube_link)

        if transcript_text:
            summary = generate_summary(transcript_text, prompt)
            if summary:
                st.markdown("## Summary:")
                st.write(summary)
