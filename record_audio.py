import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import keyboard
import threading
import assemblyai as aai
import google.generativeai as genai

# Configuration
samplerate = 44100  # Standard sampling rate
channels = 2  # Stereo audio
dtype = np.int16  # Data type for recording
output_filename = "system_audio.wav"
transcription_filename = "transcription.txt"
summary_filename = "summary.txt"

# API Keys (Replace with your actual keys)
ASSEMBLYAI_API_KEY = "ad0432a4de464cab9ff0709c13b2438c"
GEMINI_API_KEY = "AIzaSyCffP0aGrU7cXR_w_uSuBhk4jMyfBTsUpM"

recording = []
is_recording = True

# Initialize AssemblyAI
aai.settings.api_key = ASSEMBLYAI_API_KEY

def record_audio():
    """Records system audio until Enter is pressed."""
    global recording, is_recording
    print("🎙️ Recording... Press 'Enter' to stop.")
    
    with sd.InputStream(samplerate=samplerate, channels=channels, dtype=dtype) as stream:
        while is_recording:
            data, _ = stream.read(1024)  # Read small chunks
            recording.append(data)

def stop_recording():
    """Stops recording when the user presses Enter."""
    global is_recording
    keyboard.wait("enter")  # Wait for Enter key
    is_recording = False
    print("\n⏹️ Stopping recording...")

# Start recording in a separate thread
record_thread = threading.Thread(target=record_audio)
record_thread.start()

# Listen for the Enter key in the main thread
stop_recording()

# Wait for recording to finish
record_thread.join()

# Save the recorded data to a WAV file
final_audio = np.concatenate(recording, axis=0)
wav.write(output_filename, samplerate, final_audio)
print(f"✅ Audio saved as {output_filename}")

def transcribe_audio():
    """Uploads audio to AssemblyAI, transcribes it, and saves the text."""
    transcriber = aai.Transcriber()
    print("\n📝 Uploading and transcribing audio...")
    
    transcript = transcriber.transcribe(output_filename)

    # Save transcription to a text file
    with open(transcription_filename, "w", encoding="utf-8") as f:
        f.write(transcript.text)

    print(f"✅ Transcription saved as {transcription_filename}")
    return transcript.text

def summarize_text(text):
    """Summarizes the transcribed text using Gemini API."""
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-pro")

    print("\n🔍 Summarizing transcript...")
    response = model.generate_content(f"Summarize this text:\n\n{text}")

    summary = response.text

    # Save summary to a file
    with open(summary_filename, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"✅ Summary saved as {summary_filename}")
    print("\n📄 Summary:\n", summary)

# Transcribe and summarize
transcribed_text = transcribe_audio()
summarize_text(transcribed_text)
