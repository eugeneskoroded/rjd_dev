import torch
import torchaudio.functional as F
import torchaudio as ta


def init_tts_model(language="ru", model_id="v4_ru", device='cuda:3'):
    model, example_text = torch.hub.load(repo_or_dir='snakers4/silero-models',
                                         model='silero_tts',
                                         language=language,
                                         speaker=model_id)
    model.to(device)
    return model


def apply_tts(model, text, sample_rate=16000, speaker='aidar', put_accent=False, put_yo=True):
    audio = model.apply_tts(text=text,
                            speaker=speaker,
                            sample_rate=48000,
                            put_accent=put_accent,
                            put_yo=put_yo)
    audio = F.resample(audio, 48000, sample_rate, lowpass_filter_width=6)
    ta.save("tts_dump.wav", audio.unsqueeze(0), sample_rate)
    return audio.numpy()
