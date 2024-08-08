import base64
import json
from flask import Flask, render_template, request
from worker import speech_to_text, text_to_speech, openai_process_message
from flask_cors import CORS
import os

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/speech-to-text', methods=['POST'])
def speech_to_text_route():
    print("Processing speech-to-text")
    audio_binary = request.data
    text = speech_to_text(audio_binary)

    response = {
        'text': text
    }
    return json.dumps(response)

@app.route('/process-message', methods=['POST'])
def process_message_route():
    # Get user message from the request
    user_message = request.json['userMessage']
    print('User message:', user_message)

    # Get selected voice from the request
    selected_voice = request.json['voice']
    print('Voice:', selected_voice)

    # Process user message using OpenAI
    openai_response_text = openai_process_message(user_message)
    # Remove empty lines from the OpenAI response
    openai_response_text = os.linesep.join([s for s in openai_response_text.splitlines() if s])

    # Convert OpenAI response text to speech
    openai_response_speech = text_to_speech(openai_response_text, selected_voice)
    # Encode the speech as base64 for transmission
    openai_response_speech = base64.b64encode(openai_response_speech).decode('utf-8')

    # Prepare the response with OpenAI response text and speech
    response = {
        "openaiResponseText": openai_response_text,
        "openaiResponseSpeech": openai_response_speech
    }
    return json.dumps(response)

if __name__ == "__main__":
    # Run the Flask app on port 8000 and allow connections from any host
    app.run(port=8000, host='0.0.0.0')
