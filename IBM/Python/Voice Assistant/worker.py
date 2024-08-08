from openai import OpenAI
import requests

openai_client = OpenAI()
# base_url = "https://sn-watson-stt.labs.skills.network"    # Speech to text
# base_url = "https://sn-watson-tts.labs.skills.network"    # Text to speech

def speech_to_text(audio_binary):
    # Set up Watson Speech-to-Text HTTP API URL
    base_url = 'https://sn-watson-stt.labs.skills.network'
    api_url = f'{base_url}/speech-to-text/api/v1/recognize'

    # Set up parameters for our HTTP request
    params = {
        'model': 'en-US_Multimedia',
    }

    # Set up the body of our HTTP request
    body = audio_binary

    # Send an HTTP POST request
    response = requests.post(api_url, params=params, data=audio_binary).json()

    # Parse the response to get our transcribed text
    text = 'null'
    while bool(response.get('results')):
        print('Speech to text response:', response)
        text = response.get('results').pop().get('alternatives').pop().get('transcript')
        print('Recognized text:', text)
        return text

def text_to_speech(text, voice=""):
    # Set up Watson Text-to-Speech HTTP API URL
    base_url = 'https://sn-watson-tts.labs.skills.network'
    api_url = f'{base_url}/text-to-speech/api/v1/synthesize?output=output_text.wav'

    # Adding voice parameter in api_url if the user has selected a preferred voice
    if voice != "" and voice != "default":
        api_url += f'&voice={voice}'

    # Set the headers for our HTTP request
    headers = {
        'Accept': 'audio/wav',
        'Content-Type': 'application/json',
    }

    # Set the body of our HTTP request
    json_data = {
        'text': text,
    }

    # Send an HTTP POST request to Watson Text-to-Speech Service
    response = requests.post(api_url, headers=headers, json=json_data)
    print('Text to speech response:', response)
    return response.content

def openai_process_message(user_message):
    # Set the prompt for OpenAI API
    prompt = "Act like a personal assistant. You can respond to questions, translate sentences, summarize news, and give recommendations."
    # Call the OpenAI API to process our prompt
    openai_response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo", 
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_message}
        ],
        max_tokens=4000
    )
    print("OpenAI response:", openai_response)
    # Parse the response to get the response message for our prompt
    response_text = openai_response.choices[0].message.content
    return response_text
