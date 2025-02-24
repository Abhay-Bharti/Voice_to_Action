import sounddevice as sd
import numpy as np
import wave
import threading
import tkinter as tk
import os
import assemblyai as aai
import google.generativeai as genai
from dotenv import load_dotenv
from datetime import datetime

# Load API keys
load_dotenv()
aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

SAMPLE_RATE = 44100  
BASE_DIR = "recordings"
if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)

MIC_DEVICE = 7  
SPEAKER_DEVICE = 6  

mic_audio_chunks = []
speaker_audio_chunks = []
recording = False  
output_file = ""

def record_mic_callback(indata, frames, time, status):
    if status:
        print(status)
    if recording:
        mic_audio_chunks.append(indata.copy())

def record_speaker_callback(indata, frames, time, status):
    if status:
        print(status)
    if recording:
        speaker_audio_chunks.append(indata.copy())

def start_recording():
    global recording, mic_audio_chunks, speaker_audio_chunks, output_file
    if recording:
        return  
    recording = True
    mic_audio_chunks = []
    speaker_audio_chunks = []
    
    timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    meeting_dir = os.path.join(BASE_DIR, f"meeting_{timestamp.replace(':', '-')}")
    if not os.path.exists(meeting_dir):
        os.makedirs(meeting_dir)
    
    output_file = os.path.join(meeting_dir, f"recording.wav")

    status_label.config(text="Recording...", fg="green")
    start_button.config(state=tk.DISABLED)
    stop_button.config(state=tk.NORMAL)

    def record():
        global recording
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype=np.int16, 
                            device=MIC_DEVICE, callback=record_mic_callback) as mic_stream, \
             sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype=np.int16, 
                            device=SPEAKER_DEVICE, callback=record_speaker_callback) as speaker_stream:
            while recording:
                sd.sleep(100)  

        process_and_save_audio()

    threading.Thread(target=record, daemon=True).start()

def stop_recording():
    global recording
    recording = False
    status_label.config(text="Recording Stopped", fg="red")
    start_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.DISABLED)

def process_and_save_audio():
    global mic_audio_chunks, speaker_audio_chunks, output_file
    
    if not mic_audio_chunks or not speaker_audio_chunks:
        status_label.config(text="No audio recorded!", fg="red")
        return
    
    mic_audio = np.concatenate(mic_audio_chunks, axis=0)
    speaker_audio = np.concatenate(speaker_audio_chunks, axis=0)

    min_length = min(len(mic_audio), len(speaker_audio))
    mic_audio = mic_audio[:min_length]
    speaker_audio = speaker_audio[:min_length]

    combined_audio = np.hstack((mic_audio, speaker_audio))

    with wave.open(output_file, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(combined_audio.tobytes())

    print(f"✅ Recording saved as {output_file}")
    status_label.config(text=f"Saved: {output_file}. Transcribing...", fg="blue")

    threading.Thread(target=run_transcription, args=(output_file,), daemon=True).start()

def run_transcription(audio_file):
    try:
        print("📝 Transcribing...")
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(audio_file).text
        transcription_file = audio_file.replace(".wav", "_transcription.txt")

        with open(transcription_file, "w", encoding="utf-8") as f:
            f.write(transcript)

        print(f"✅ Transcription saved: {transcription_file}")
        status_label.config(text="Transcription done. Summarizing...", fg="blue")

        threading.Thread(target=run_summarization, args=(transcript, audio_file), daemon=True).start()

    except Exception as e:
        print(f"⚠️ Transcription failed: {e}")
        status_label.config(text="Transcription failed!", fg="red")

def run_summarization(transcript, audio_file):
    try:
        print("📄 Summarizing...")
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(f"Summarize this text as a meeting and also give important points as bullet points and also make todo list for any upcoming event or upcoming meetings:\n\n{transcript}")
        summary = response.text
        summary_file = audio_file.replace(".wav", "_summary.txt")

        with open(summary_file, "w", encoding="utf-8") as f:
            f.write(summary)

        print(f"✅ Summary saved: {summary_file}")
        status_label.config(text="Summarization complete!", fg="green")

    except Exception as e:
        print(f"⚠️ Summarization failed: {e}")
        status_label.config(text="Summarization failed!", fg="red")

# GUI Setup
root = tk.Tk()
root.title("Meeting Transcriber")
root.geometry("1000x500")
root.configure(bg="#f0f0f0")

status_label = tk.Label(root, text="Press Start to Record", font=("Arial", 14, "bold"), fg="#333", bg="#f0f0f0")
status_label.pack(pady=15)

# Start Button
start_button = tk.Button(
    root, text="Start Recording", font=("Arial", 12, "bold"),
    command=start_recording, bg="#28a745", fg="black",
    width=20, height=2
)
start_button.pack(pady=10)

# Stop Button
stop_button = tk.Button(
    root, text="Stop Recording", font=("Arial", 12, "bold"),
    command=stop_recording, bg="#ff6666", fg="black",
    width=20, height=2, state=tk.DISABLED
)
stop_button.pack(pady=10)

root.mainloop()
