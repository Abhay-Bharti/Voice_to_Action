# Meeting Recorder

## Overview
Meeting Recorder is a Python-based application that records both microphone and speaker audio during meetings, transcribes the audio using AssemblyAI, and generates a summary using Google's Gemini AI. The application comes with a simple Tkinter GUI for easy usage.

## Features
- **Record Audio:** Captures both microphone and speaker audio.
- **Transcription:** Uses AssemblyAI to transcribe speech into text.
- **Summarization:** Generates a summary of the transcribed text using Gemini AI.
- **GUI Interface:** Simple and user-friendly Tkinter interface.
- **File Management:** Saves recordings and transcriptions in an organized folder structure.

## Installation

### Prerequisites
Ensure you have Python installed (Python 3.x recommended). Install required dependencies using:

```sh
pip install sounddevice numpy wave assemblyai google-generativeai python-dotenv tkinter
```

### API Keys
1. Get an API key from [AssemblyAI](https://www.assemblyai.com/).
2. Get an API key from [Google Gemini AI](https://ai.google.dev/).
3. Create a `.env` file in the project directory and add:

```
ASSEMBLYAI_API_KEY=your_assemblyai_api_key
GEMINI_API_KEY=your_gemini_api_key
```

## Usage
Run the application using:

```sh
python main.py
```

### Creating a Desktop Shortcut (Windows)
1. **Convert Python Script to Executable (Optional)**:
   ```sh
   pip install pyinstaller
   pyinstaller --onefile --windowed MeetingRecorder.py
   ```
2. Move the `.exe` file from the `dist/` folder to a convenient location.
3. **Create a Shortcut**:
   - Right-click on Desktop → New → Shortcut.
   - Browse to the `.exe` file and select it.
   - Click **Next**, name it "Meeting Recorder", and click **Finish**.

### For macOS/Linux
Follow instructions in the main project documentation for setting up `.command` or `.desktop` files.

## File Structure
```
Meeting Recorder/
│-- main.py
│-- recordings/
│   │-- meeting_01-01-2025 12-30-00/
│   │   ├── recording.wav
│   │   ├── recording_transcription.txt
│   │   ├── recording_summary.txt
│-- .env
│-- README.md
```

## Contributing
If you'd like to contribute, feel free to fork the repo and submit a pull request!

**Enjoy using Meeting Recorder! 🚀**

