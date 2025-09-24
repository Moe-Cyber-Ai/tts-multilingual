import io  # Works with all examples and integrated with new web page
import threading
from flask import Flask, request, Response, jsonify
from flask_cors import CORS
from langdetect import detect_langs, DetectorFactory
from gtts import gTTS
import langid
import asyncio
from edge_tts import Communicate

DetectorFactory.seed = 0  # Ensures consistent results

app = Flask(__name__)
CORS(app)
# Languages prioritized for detection
PRIORITY_LANGUAGES = {"en", "de", "ru", "tr"}
ALLOWED_LANGUAGES = PRIORITY_LANGUAGES.copy()
# ----------- Language Detection -----------


def detect_language(text):
    try:
        detected = detect_langs(text)
        lang_probs = {d.lang: d.prob for d in detected}
        for lang in PRIORITY_LANGUAGES:
            if lang in lang_probs and lang_probs[lang] > 0.8:
                return lang
        lang, confidence = langid.classify(text)
        return lang if lang in ALLOWED_LANGUAGES else "unknown"
    except Exception:
        return "unknown"


def split_text_by_word_groups(text, group_size=4):
    words = text.strip().split()
    return [" ".join(words[i:i + group_size]) for i in range(0, len(words), group_size)]


def process_word_groups(groups):
    ordered_segments = []
    prev_lang = None
    temp_segment = []
    detected_languages = []

    for group in groups:
        lang = detect_language(group)
        detected_languages.append((group, lang))

        if lang == prev_lang or prev_lang is None:
            temp_segment.append(group)
        else:
            ordered_segments.append((prev_lang, " ".join(temp_segment)))
            temp_segment = [group]
        prev_lang = lang

    if temp_segment:
        ordered_segments.append((prev_lang, " ".join(temp_segment)))

    return ordered_segments, detected_languages

# ----------- General TTS Streaming -----------


def generate_audio_stream(sentences):
    audio_buffers = []
    threads = []

    def process_segment(lang, segment, index):
        try:
            audio_buffer = io.BytesIO()
            if lang == "en":
                communicate = Communicate(
                    text=segment, voice="en-US-GuyNeural", rate="-10%")
                stream = communicate.stream()

                async def collect():
                    result = b""
                    async for chunk in stream:
                        if chunk["type"] == "audio":
                            result += chunk["data"]
                    return result

                audio_data = asyncio.run(collect())
                audio_buffer.write(audio_data)
            else:
                tts = gTTS(text=segment, lang=lang)
                tts.write_to_fp(audio_buffer)

            audio_buffer.seek(0)
            audio_buffers.append((index, audio_buffer.read()))
        except Exception as e:
            print(f"Segment error: {e}")

    for i, (lang, segment) in enumerate(sentences):
        thread = threading.Thread(
            target=process_segment, args=(lang, segment, i))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    for _, audio_data in sorted(audio_buffers):
        yield audio_data

# ----------- Routes -----------


@app.route('/tts', methods=['POST'])
def text_to_speech():
    try:
        text = request.form.get("text", "").strip()
        if not text:
            return jsonify({"error": "No text provided"}), 400

        word_groups = split_text_by_word_groups(text)
        ordered_segments, detected_languages = process_word_groups(word_groups)

        if not ordered_segments:
            return jsonify({"error": "No valid language segments detected"}), 400

        return Response(generate_audio_stream(ordered_segments), mimetype="audio/mpeg"), 200, {
            "X-Debug-Languages": str(detected_languages).encode('unicode_escape').decode('utf-8')
        }
    except Exception:
        return jsonify({"error": "Internal Server Error"}), 500


@app.route('/tts_german_lesson', methods=['POST'])
def tts_german_lesson():
    try:
        text = request.form.get("text", "").strip()
        if not text:
            return jsonify({"error": "No text provided"}), 400

        word_groups = split_text_by_word_groups(text)
        ordered_segments, _ = process_word_groups(word_groups)
        langs_used = set(lang for lang, _ in ordered_segments)

        if not ("en" in langs_used and "de" in langs_used):
            return jsonify({"error": "German lesson requires both English and German"}), 400

        def generate_german_stream():
            for lang, segment in ordered_segments:
                if lang == "en":
                    communicate = Communicate(
                        text=segment, voice="en-US-GuyNeural", rate="-10%")
                    stream = communicate.stream()

                    async def collect():
                        result = b""
                        async for chunk in stream:
                            if chunk["type"] == "audio":
                                result += chunk["data"]
                        return result

                    audio_data = asyncio.run(collect())
                    yield audio_data
                elif lang == "de":
                    buffer = io.BytesIO()
                    tts = gTTS(text=segment, lang="de")
                    tts.write_to_fp(buffer)
                    buffer.seek(0)
                    yield buffer.read()

        return Response(generate_german_stream(), mimetype="audio/mpeg")
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/tts_russian_lesson', methods=['POST'])
def tts_russian_lesson():
    try:
        text = request.form.get("text", "").strip()
        if not text:
            return jsonify({"error": "No text provided"}), 400

        word_groups = split_text_by_word_groups(text)
        ordered_segments, _ = process_word_groups(word_groups)
        langs_used = set(lang for lang, _ in ordered_segments)

        if not ("en" in langs_used and "ru" in langs_used):
            return jsonify({"error": "Russian lesson requires both English and Russian"}), 400

        def generate_russian_stream():
            for lang, segment in ordered_segments:
                if lang == "en":
                    communicate = Communicate(
                        text=segment, voice="en-US-GuyNeural", rate="-10%")
                    stream = communicate.stream()

                    async def collect():
                        result = b""
                        async for chunk in stream:
                            if chunk["type"] == "audio":
                                result += chunk["data"]
                        return result

                    audio_data = asyncio.run(collect())
                    yield audio_data
                elif lang == "ru":
                    buffer = io.BytesIO()
                    tts = gTTS(text=segment, lang="ru")
                    tts.write_to_fp(buffer)
                    buffer.seek(0)
                    yield buffer.read()

        return Response(generate_russian_stream(), mimetype="audio/mpeg")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ----------- Run Server -----------


if __name__ == '__main__':
    app.run(debug=True)
