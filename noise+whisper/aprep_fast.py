
from warnings import filterwarnings
from typing import Union
from fastapi import FastAPI, Request, UploadFile, File, Response
from fastapi.middleware.cors import CORSMiddleware
import noise_anr as nr
import whisperx_asr as wx
import base64
import numpy as np
import tts
import re
from num2words import num2words
from transliterate import translit
import json

filterwarnings("ignore")
# MICRO_TCN_PARAMS
MODEL_DIR_ = "./micro-tcn/"  # Location of models folder
MODEL_ID_ = "9-uTCN-300__causal__4-10-13__fraction-0.1-bs32"  # Model_id
# WAV_PATH_ = "/content/src/cut_0.wav"  # Path to folder of wav or wav file
GPU_ = True  # True: use GPU, False: use CPU

# WHISPER PARAMS
WHISPER_ARCH_ = 'large-v2'
LANGUAGE_CODE_ = 'ru'
DEVICE_ = 'cuda'

# TTS PARAMS
TTS_LANGUAGE = "ru"
TTS_MODEL_ID = "v4_ru"
TTS_DEVICE = 'cuda:3'
SAMPLE_RATE = 16000
SPEAKER = 'aidar'
# DFN PARAMS

# INIT TCN MODEL
tcn_model = nr.init_tcn_model(MODEL_DIR_, MODEL_ID_, gpu=GPU_)

# INIT WHISPER MODEL
whisper_model_ = wx.init_asr_model(
    WHISPER_ARCH_, DEVICE_, asr_opt={"initial_prompt": None})

# INIT TTS MODEL
tts_model = tts.init_tts_model(
    language=TTS_LANGUAGE, model_id=TTS_MODEL_ID, device=TTS_DEVICE)

# INIT DFN MODEL
dfn_model = nr. init_dfn_model()
# uvicorn aprep_fast:app --reload --host "0.0.0.0" --port 8081

# ADDITIONAL FUNCTIONS


def seg_comb(data):  # clean whisperx json format
    text = []
    for seg in data['segments']:
        text.append(seg['text'])
    text = '.'.join(text)
    print(text)
    return text


def string_conv(string):  # convert numbers to str and en chars to ru
    numbers = re.findall(r'\d+', string)
    numbers.sort(key=len, reverse=True)
    number_in_words = []
    for i in range(len(numbers)):
        number_in_words.append(num2words(numbers[i], lang='ru'))
    for i in range(len(numbers)):
        string = string.replace(numbers[i], f' {number_in_words[i]} ')
    ru_string = translit(string, 'ru')
    return (ru_string)


# FASTAPI
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
    audio_ = wx.load_audio(contents)
    audio_ = np.insert(audio_, 0, np.zeros(24000)).tobytes()
    return Response(content=contents)
# @app.post("/audio_load")
# async def audio_load(file: UploadFile = File(...)):
#     contents = await file.read()
#     encoded_contents = base64.b64encode(contents).decode('utf-8')
#     return {"content": encoded_contents}


@app.post("/audio")
async def audio_upload(file: UploadFile = File(...)):
    if file is not None:
        contents = await file.read()
        audio_ = wx.load_audio(contents)
        print(audio_)
        return {"filename": file.filename}
    else:
        return "ERROR: Request must contain audio file"


@app.post("/send_message")
async def send_message(message: Request):
    data = await message.json()
    filename = "tts_dump.wav"
    with open(filename, 'rb') as f:
        file = f.read()
    file = base64.b64encode(file).decode("utf-8")
    print("[LOG]/send_message: ", data)
    out_mess = {"answer": "Опять работа?", "tts_file": file}
    return out_mess


@app.post("/speech_to_text")
async def speech_to_text(file: UploadFile = File(...)):
    if file is not None:
        contents = await file.read()
        audio_ = wx.load_audio(contents)
        if len(audio_) < 24000:
            return "ОШИБКА! Отправьте новое голосовое сообщение"
        audio_ = np.insert(audio_, 0, np.zeros(24000))
        tcn_result = nr.wav_nr_buffer(
            audio_, tcn_model, dfn_model, gpu=GPU_, verbose=True)
        print(tcn_result)
        whisper_result = wx.asr_model_transcribe(
            asr_model=whisper_model_, audio_file=tcn_result)
        print("[LOG] /speech_to_text:", whisper_result)
        result = seg_comb(whisper_result)
        return result
    else:
        return "ERROR: Request must contain audio file"


@app.post("/stt_tts")
async def speech_to_text(file: UploadFile = File(...)):
    if file is not None:
        contents = await file.read()
        audio_ = wx.load_audio(contents)
        audio_ = np.insert(audio_, 0, np.zeros(24000))
        tcn_result = nr.wav_nr_buffer(
            audio_, tcn_model, dfn_model, gpu=GPU_, verbose=True)

        whisper_result = wx.asr_model_transcribe(
            asr_model=whisper_model_, audio_file=tcn_result)

        result = string_conv(seg_comb(whisper_result))

        tts_res = tts.apply_tts(
            tts_model, result, sample_rate=SAMPLE_RATE, speaker=SPEAKER)

        return result
    else:
        return "ERROR: Request must contain audio file"


def llama_pipeline(jsonResult):
    return jsonResult
