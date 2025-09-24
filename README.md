# tts-multilingual
This project is a Flask-based text-to-speech (TTS) API that automatically detects multiple languages in text, splits it into language-specific segments, and streams back generated speech audio.
Features

Automatic Language Detection
Uses langdetect + langid to detect languages in each text segment.

Multilingual TTS

English speech via Microsoft Edge Neural Voices (edge-tts)
Other supported languages via gTTS
Streaming Output
Audio is streamed back progressively for lower latency.

Lesson-Specific Endpoints
/tts_german_lesson – requires both English & German text
/tts_russian_lesson – requires both English & Russian text

Ready to use with frontend apps or web pages.

Installation
1. Clone the repository
git clone https://github.com/<your-username>/<your-repo-name>.git
cd <your-repo-name>

2. Create and activate a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install dependencies
pip install -r requirements.txt


Create a requirements.txt file with:

Flask
flask-cors
langdetect
langid
gTTS
edge-tts

Usage
Run the Flask server:
python app.py
By default, it will start on http://127.0.0.1:5000/.

API Endpoints
POST /tts

General text-to-speech endpoint.

Request
{
  "text": "Hello this is English. Hallo das ist Deutsch."
}
Response
audio/mpeg stream of generated speech.

Response header X-Debug-Languages shows detected languages per segment.

POST /tts_german_lesson

Text-to-speech specifically for German lessons.
Requires at least one English and one German segment.

POST /tts_russian_lesson

Text-to-speech specifically for Russian lessons.
Requires at least one English and one Russian segment.

Example cURL Request
curl -X POST http://127.0.0.1:5000/tts \
  -F "text=Hello this is English. Hallo das ist Deutsch." \
  --output output.mp3
Notes
Edge-TTS requires an internet connection (uses Microsoft Neural TTS voices).
gTTS also requires internet access (uses Google Translate TTS).
For production, consider running Flask with a WSGI server like gunicorn.
