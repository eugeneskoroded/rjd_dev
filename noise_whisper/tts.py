import torch
import torchaudio.functional as F
import torchaudio as ta
from spacy.lang.ru import Russian


cuda_available = torch.cuda.is_available()
print(cuda_available)

def init_tts_model(language="ru", model_id="v4_ru", device='cuda:0'):
    model, example_text = torch.hub.load(repo_or_dir='snakers4/silero-models',
                                         model='silero_tts',
                                         language=language,
                                         speaker=model_id)
    model.to(device)
    return model


def split_string(string, max_len=100):
    if len(string) <= max_len:
        return [string]
    else:
        result = []
        i = 0
        while i < len(string):
            result.append(string[i : i + max_len])
            i += max_len
        return result
        

def apply_tts(model, text, sample_rate=16000, speaker='aidar', put_accent=False, put_yo=True):
    if len(text) < 1000:
        audio = model.apply_tts(text=text,
                                speaker=speaker,
                                sample_rate=48000,
                                put_accent=put_accent,
                                put_yo=put_yo)
        audio = F.resample(audio, 48000, sample_rate, lowpass_filter_width=6)
    else:
        chunks = []
        nlp = Russian()
        doc = nlp(text)
        chunk = []
        for token in doc:
            if len(' '.join(chunk)) < 950:
                chunk.append(token.text)
            else:
                chunks.append(' '.join(chunk))
                chunk = []
                chunk.append(token.text)
        print(chunks)
        t_chunks = []
        for c in chunks:
            audio = model.apply_tts(text=c,
                                speaker=speaker,
                                sample_rate=48000,
                                put_accent=put_accent,
                                put_yo=put_yo)
            audio = F.resample(audio, 48000, sample_rate, lowpass_filter_width=6)
            t_chunks.append(audio)
        audio = torch.cat(t_chunks, 0)
    ta.save("tts_dump.wav", audio.unsqueeze(0), sample_rate-1000)
    return audio.numpy()
