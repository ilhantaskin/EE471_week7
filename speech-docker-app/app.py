import os
import uuid
from flask import Flask, render_template, request, send_from_directory
from dotenv import load_dotenv
import azure.cognitiveservices.speech as speechsdk

load_dotenv(dotenv_path=".env")

app = Flask(__name__)

SPEECH_KEY = os.getenv("SPEECH_KEY")
SPEECH_REGION = os.getenv("SPEECH_REGION")

UPLOAD_FOLDER = "static/uploads"
OUTPUT_FOLDER = "static/outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/text-to-speech", methods=["POST"])
def text_to_speech():
    text = request.form.get("text", "").strip()

    if not text:
        return render_template("index.html", tts_error="Please enter text.")

    output_filename = f"{uuid.uuid4()}.wav"
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)

    speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
    audio_config = speechsdk.audio.AudioOutputConfig(filename=output_path)

    synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config,
        audio_config=audio_config
    )

    result = synthesizer.speak_text_async(text).get()

    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        return render_template(
            "index.html",
            tts_success="Speech synthesized successfully.",
            audio_file=output_filename
        )

    return render_template("index.html", tts_error="Text-to-speech failed.")

@app.route("/speech-to-text", methods=["POST"])
def speech_to_text():
    if "audio" not in request.files:
        return render_template("index.html", stt_error="Please upload an audio file.")

    audio_file = request.files["audio"]

    if audio_file.filename == "":
        return render_template("index.html", stt_error="No file selected.")

    saved_filename = f"{uuid.uuid4()}_{audio_file.filename}"
    saved_path = os.path.join(UPLOAD_FOLDER, saved_filename)
    audio_file.save(saved_path)

    speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
    audio_input = speechsdk.audio.AudioConfig(filename=saved_path)

    recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config,
        audio_config=audio_input
    )

    result = recognizer.recognize_once_async().get()

    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        return render_template(
            "index.html",
            stt_success="Audio transcribed successfully.",
            transcription=result.text
        )

    return render_template("index.html", stt_error="Speech-to-text failed.")

@app.route("/audio/<filename>")
def audio_file(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)