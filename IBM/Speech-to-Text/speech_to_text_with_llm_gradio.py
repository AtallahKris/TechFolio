import torch
import os
import gradio as gr
from transformers import pipeline
from langchain.llms import HuggingFaceHub
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from ibm_watson_machine_learning.foundation_models import Model
from ibm_watson_machine_learning.foundation_models.extensions.langchain import WatsonxLLM
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams

my_credentials = {
    "url": "https://us-south.ml.cloud.ibm.com"
}
params = {
    GenParams.MAX_NEW_TOKENS: 800,  # The maximum number of tokens that the model can generate in a single run.
    GenParams.TEMPERATURE: 0.1,  # A parameter that controls the randomness of the token generation. A lower value makes the generation more deterministic, while a higher value introduces more randomness.
}

llama2_model = Model(
    model_id='meta-llama/llama-2-70b-chat',
    credentials=my_credentials,
    params=params,
    project_id="skills-network",
)

llm = WatsonxLLM(llama2_model)

# Prompt Template

template = """
<s><<SYS>>
List the key points with details from the context: 
[INST] The context : {context} [/INST] 
<</SYS>>
"""

prompt_template = PromptTemplate(
    input_variables=["context"],
    template=template
)

prompt_to_llama2 = LLMChain(llm=llm, prompt=prompt_template)

# Speech-to-Text Function

def transcript_audio(audio_file):
    # Initialize the speech recognition pipeline
    speech_recognition_pipeline = pipeline(
        "automatic-speech-recognition",
        model="openai/whisper-tiny.en",
        chunk_length_s=30,
    )
    # Transcribe the audio file and return the result
    transcript_txt = speech_recognition_pipeline(audio_file, batch_size=8)["text"]
    result = prompt_to_llama2.run(transcript_txt)

    return result

# Gradio Interface

audio_input = gr.Audio(sources="upload", type="filepath")
output_text = gr.Textbox()

interface = gr.Interface(
    fn=transcript_audio,
    inputs=audio_input,
    outputs=output_text,
    title="Audio Transcription App",
    description="Upload the audio file"
)

interface.launch(server_name="0.0.0.0", server_port=7860)
