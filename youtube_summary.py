import re
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import torch
import gradio as gr
from transformers import pipeline

# Initialize the summarization pipeline
text_summary = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6", torch_dtype=torch.bfloat16)

def chunk_text(input_text, max_chunk_size=1024):
    """
    Splits the input text into smaller chunks of size `max_chunk_size` or smaller.
    """
    words = input_text.split()
    chunks = []
    current_chunk = []

    for word in words:
        if len(" ".join(current_chunk + [word])) <= max_chunk_size:
            current_chunk.append(word)
        else:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
    
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks

def summary(input):
    """
    Generates a summary for a given input text.
    """
    output = text_summary(input)
    return output[0]['summary_text']

def extract_video_id(url):
    """
    Extracts the video ID from various YouTube URL formats.
    """
    regex = r"(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})"
    match = re.search(regex, url)
    if match:
        return match.group(1)
    return None

def get_youtube_transcript(video_url):
    """
    Fetches the YouTube video transcript, splits it into chunks, summarizes it, and combines the summaries.
    """
    video_id = extract_video_id(video_url)
    if not video_id:
        return "Video ID could not be extracted."

    try:
        # Fetch the transcript
        transcript = YouTubeTranscriptApi.get_transcript(video_id)

        # Format the transcript into plain text
        formatter = TextFormatter()
        text_transcript = formatter.format_transcript(transcript)

        # Chunk the transcript and summarize each chunk
        chunks = chunk_text(text_transcript, max_chunk_size=1024)
        chunk_summaries = [summary(chunk) for chunk in chunks]

        # Combine chunk summaries into a final summary
        final_summary = " ".join(chunk_summaries)
        return final_summary
    except Exception as e:
        return f"An error occurred: {e}"

# Gradio Interface
gr.close_all()

demo = gr.Interface(
    fn=get_youtube_transcript,
    inputs=[gr.Textbox(label="Input YouTube Url to summarize", lines=1)],
    outputs=[gr.Textbox(label="Summarized text", lines=4)],
    title="YOUTUBE SCRIPT SUMMARIZER",
    description="THIS APPLICATION WILL BE USED TO SUMMARIZE THE YOUTUBE VIDEO SCRIPT."
)
demo.launch()
