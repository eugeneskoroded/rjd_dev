import os
import json
from warnings import filterwarnings
from typing import Union
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from pydantic import BaseModel
import noise_anr as nr
import whisperx_asr as wx
import uvicorn

MODEL_DIR_ = "./micro-tcn/"  # Location of models folder
MODEL_ID_ = "9-uTCN-300__causal__4-10-13__fraction-0.1-bs32"  # Model_id
# WAV_PATH_ = "/content/src/cut_0.wav"  # Path to folder of wav or wav file
GPU_ = True  # True: use GPU, False: use CPU

WHISPER_ARCH_ = 'large-v2'
LANGUAGE_CODE_ = 'ru'
DEVICE_ = 'cuda'


tcn_model = nr.init_tcn_model(MODEL_DIR_, MODEL_ID_, gpu=GPU_)
initial_prompt = None
whisper_model_ = wx.init_asr_model(WHISPER_ARCH_, DEVICE_, asr_opt={
    "initial_prompt": initial_prompt})
# uvicorn main:app --reload --port 1234
app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/audio_load")
async def audio_load(audio_buffer: Request):
    data = await audio_buffer.json()
    print(data)
    return data


@app.post("/shit")
async def shit(audio_buffer):
    print(audio)
    return audio_buffer


@app.post("/speech_to_text")
async def speech_to_text(audio_buffer: Request):
    data = await audio_buffer.json()
    audio_ = nr.load_audio(data)
    tcn_result = nr.wav_nr_buffer(audio_, tcn_model, gpu=GPU_, verbose=True)
    whisper_result = wx.asr_model_transcribe(
        asr_model=whisper_model_, audio_file=tcn_result)
    jsonResult = json.dumps(whisper_result)
    res = await llama_pipeline(jsonResult)
    # Впихнуть ттс
    return res


def llama_pipeline(jsonResult):
    return jsonResult