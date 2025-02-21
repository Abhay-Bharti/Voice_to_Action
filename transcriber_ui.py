import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import threading
import assemblyai as aai
import google.generativeai as genai
import tkinter as tk
from tkinter import messagebox
import os
import datetime

# Configuration
samplerate = 44100  # Standard sampling rate
channels = 2  # Stereo audio
dtype = np.int16  # Data type for recording

# API Keys (Replace with your actual keys)
ASSEMBLYAI_API_KEY = "your_assemblyai_api_key"
GEMINI_API_KEY = "your_gemini_api_key"

# Initialize AssemblyAI
aai.settings.api_key = ASSEMBLYAI_API_KEY

# Ensure directories exist
os.makedirs("recordings", exist_ok=True)
os.makedirs("transcriptions", exist_ok=True)
os.makedirs("summaries", exist_ok=True)

recording = []
is_recording = False

def get_timestamp():
    """Returns current timestamp in DD-MM-YYYY format."""
    return datetime.datetime.now().strftime("%d-%m-%Y")

def record_audio():
    """Records system audio until 'Stop Recording' is pressed."""
    global recording, is_recording
    is_recording = True
    recording.clear()

    with sd.InputStream(samplerate=samplerate, channels=channels, dtype=dtype) as stream:
        while is_recording:
            data, _ = stream.read(1024)  # Read small chunks
            recording.append(data)

def start_recording():
    """Starts recording in a separate thread."""
    global record_thread
    record_thread = threading.Thread(target=record_audio)
    record_thread.start()
    
    start_button.config(state=tk.DISABLED)
    stop_button.config(state=tk.NORMAL)
    status_label.config(text="Recording...")

def stop_recording():
    """Stops recording, saves audio file, and triggers transcription."""
    global is_recording
    is_recording = False
    record_thread.join()

    timestamp = get_timestamp()
    audio_filename = f"recordings/meeting-{timestamp}.wav"
    
    # Save the recorded data to a WAV file
    final_audio = np.concatenate(recording, axis=0)
    wav.write(audio_filename, samplerate, final_audio)

    start_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.DISABLED)
    status_label.config(text="Recording Stopped")
    messagebox.showinfo("Recording Saved", f"Audio saved as {audio_filename}")

    # Automatically transcribe & summarize
    transcribe_audio(audio_filename, timestamp)

def transcribe_audio(audio_filename, timestamp):
    """Uploads audio to AssemblyAI, transcribes it, and saves the text."""
    transcriber = aai.Transcriber()
    status_label.config(text="Transcribing...")

    try:
        transcript = transcriber.transcribe(audio_filename)

        transcript_filename = f"transcriptions/meeting-{timestamp}.txt"
        with open(transcript_filename, "w", encoding="utf-8") as f:
            f.write(transcript.text)

        status_label.config(text="Transcription Complete")
        messagebox.showinfo("Transcription Complete", f"Saved as {transcript_filename}")

        # Automatically summarize
        summarize_text(transcript.text, timestamp)

    except Exception as e:
        messagebox.showerror("Error", f"Transcription Failed: {e}")

def summarize_text(text, timestamp):
    """Summarizes the transcribed text using Gemini API and saves the summary."""
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-pro")

        status_label.config(text="Summarizing...")
        response = model.generate_content(f"Summarize this text:\n\n{text}")

        summary_filename = f"summaries/meeting-{timestamp}.txt"
        with open(summary_filename, "w", encoding="utf-8") as f:
            f.write(response.text)

        status_label.config(text="Summary Complete")
        messagebox.showinfo("Summary Complete", f"Saved as {summary_filename}")

    except Exception as e:
        messagebox.showerror("Error", f"Summarization Failed: {e}")

# UI Setup
root = tk.Tk()
root.title("Audio Transcriber & Summarizer")
root.geometry("400x300")

status_label = tk.Label(root, text="Press 'Start Recording' to begin", font=("Arial", 12))
status_label.pack(pady=10)

start_button = tk.Button(root, text="Start Recording", font=("Arial", 12), bg="green", fg="white", command=start_recording)
start_button.pack(pady=5)

stop_button = tk.Button(root, text="Stop Recording", font=("Arial", 12), bg="red", fg="white", command=stop_recording, state=tk.DISABLED)
stop_button.pack(pady=5)

root.mainloop()
