import os
import json
import shutil
from warnings import filterwarnings
from typing import Union
from fastapi import FastAPI, Request, UploadFile, File, Body
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from starlette.responses import Response
from pydantic import BaseModel
import noise_anr as nr
import whisperx_asr as wx
import uvicorn
from io import BytesIO
import base64
import numpy as np
import ujson
from requests import Session
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
# uvicorn aprep_fast:app --reload --host "0.0.0.0" --port 8081


def seg_comb(data):
    text = []
    for seg in data['segments']:
        text.append(seg['text'])
    text = '.'.join(text)
    print(text)
    return text


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
async def audio_load(file: UploadFile = File(...)):
    contents = await file.read()
    encoded_contents = base64.b64encode(contents).decode('utf-8')
    return {"content": encoded_contents}


@app.post("/audio")
async def audio_upload(file: UploadFile = File(...)):
    if file is not None:
        contents = await file.read()
        audio_ = wx.load_audio(contents)
        print(audio_)
        return {"filename": file.filename}
    else:
        return "sas"


@app.post("/speech_to_text")
async def speech_to_text(file: UploadFile = File(...)):
    if file is not None:
        contents = await file.read()
        audio_ = wx.load_audio(contents)
        tcn_result = nr.wav_nr_buffer(
            audio_, tcn_model, gpu=GPU_, verbose=True)
        whisper_result = wx.asr_model_transcribe(
            asr_model=whisper_model_, audio_file=tcn_result)
        print(whisper_result)
        result = seg_comb(whisper_result)
        return result
    else:
        return "ERROR: Request must contain audio file"

# res = await llama_pipeline(jsonResult)
 # Впихнуть ттс


def llama_pipeline(jsonResult):
    return jsonResult
