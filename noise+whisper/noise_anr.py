import numpy as np
import os
import subprocess
import ffmpeg
import sys
import glob
import time
import torch
import itertools
import torchaudio
from microtcn.tcn import TCNModel
from microtcn.lstm import LSTMModel
from df.enhance import enhance, init_df, save_audio
import torchaudio.functional as F

torchaudio.set_audio_backend("sox_io")


def convert_to_wav(input_file: str, ffmpeg_ar: str = '16000', ffmpeg_acodec: str = 'pcm_s16le', ffmpeg_ac: str = '1',
                   output_file: str = None) -> str:
    """
    Converts an audio file to WAV format using FFmpeg.

    Args:
        input_file: The path of the input audio file to convert.
        ffmpeg_ar: audio rate (Hz) of output WAV file.
        ffmpeg_acodec: audio codec of output WAV file.
        ffmpeg_ac: audio channels of output WAV file.
        output_file: The path of the output WAV file. If None, the output file will be created by replacing
                     the input file extension with ".wav".

    Returns:
        None
    """
    if not output_file:
        output_file = os.path.splitext(input_file)[0] + ".wav"

    command = f'ffmpeg -i "{input_file}" -vn -acodec {ffmpeg_acodec} -ar {ffmpeg_ar} -ac {ffmpeg_ac} "{output_file}"'

    try:
        subprocess.run(command, shell=True, check=True)
        print(f'Successfully converted "{input_file}" to "{output_file}"')
    except subprocess.CalledProcessError as e:
        print(
            f'Error: {e}, could not convert "{input_file}" to "{output_file}"')

    return output_file


def convert_to_aac(input_file: str, ffmpeg_ar: str = '16000', ffmpeg_acodec: str = 'pcm_s16le', ffmpeg_ac: str = '1',
                   output_file: str = None) -> str:
    """
    Converts an audio file to WAV format using FFmpeg.

    Args:
        input_file: The path of the input audio file to convert.
        ffmpeg_ar: audio rate (Hz) of output WAV file.
        ffmpeg_acodec: audio codec of output WAV file.
        ffmpeg_ac: audio channels of output WAV file.
        output_file: The path of the output WAV file. If None, the output file will be created by replacing
                     the input file extension with ".aac".

    Returns:
        None
    """
    if not output_file:
        output_file = os.path.splitext(input_file)[0] + ".aac"

    command = f'ffmpeg -i "{input_file}" -vn -acodec {ffmpeg_acodec} -ar {ffmpeg_ar} -ac {ffmpeg_ac} "{output_file}"'

    try:
        subprocess.run(command, shell=True, check=True)
        print(f'Successfully converted "{input_file}" to "{output_file}"')
    except subprocess.CalledProcessError as e:
        print(
            f'Error: {e}, could not convert "{input_file}" to "{output_file}"')

    return output_file


def load_audio(file: (str, bytes), sr: int = 24000):
    """
    Open an audio file and read as mono waveform, resampling as necessary

    Parameters
    ----------
    file: (str, bytes)
        The audio file to open or bytes of audio file

    sr: int
        The sample rate to resample the audio if necessary

    Returns
    -------
    A NumPy array containing the audio waveform, in float32 dtype.
    """

    if isinstance(file, bytes):
        inp = file
        file = 'pipe:'
    else:
        inp = None

    try:
        # This launches a subprocess to decode audio while down-mixing and resampling as necessary.
        # Requires the ffmpeg CLI and `ffmpeg-python` package to be installed.
        out, _ = (
            ffmpeg.input(file, threads=0)
            .output("-", format="s16le", acodec="pcm_s16le", ac=1, ar=sr)
            .run(cmd="ffmpeg", capture_stdout=True, capture_stderr=True, input=inp)
        )
    except ffmpeg.Error as e:
        raise RuntimeError(f"Failed to load audio: {e.stderr.decode()}") from e

    return np.frombuffer(out, np.int16).flatten().astype(np.float32)


def convert_to_waveform(ar):
    return torch.from_numpy(ar).unsqueeze(0)


def wav_to_aac(file: str, sr: int = 24000):
    pass


def get_files(input):
    if input is not None:
        if os.path.isdir(input):
            inputfiles = glob.glob(os.path.join(input, "*"))
        elif os.path.isfile(input):
            inputfiles = [input]
        else:
            raise RuntimeError(f" '{input}' is not a valid file!")
    print(f"Found {len(inputfiles)} input file(s).")

    return inputfiles


def tcn_dfn_process_args(inputfile, out_path, model_tcn, model_dfn, limit=0.1, peak_red=0.5, gpu=False, verbose=True, noise_reducer=True):
    input, sr = torchaudio.load(inputfile, normalize=False)
    input = input.float() / 32768  # 32768
    # check if the input is mono
    if input.size(0) > 1:
        print(
            f"Warning: Model only supports mono audio, will downmix {input.size(0)} channels.")
        input = torch.sum(input, dim=0)

    # we will resample here if needed
    if sr != 44100:
        print(
            f"Warning: Model only operates at 44.1 kHz, will resample from {sr} Hz.")

    # construct conditioning
    params = torch.tensor([limit, peak_red])

    # add batch dimension
    input = input.view(1, 1, -1)
    params = params.view(1, 1, 2)

    # move to GPU
    if gpu:
        input = input.to("cuda:0")
        params = params.to("cuda:0")
        model_tcn.to("cuda:0")

    # pass through model
    tic = time.perf_counter()
    out = model_tcn(input, params).view(1, -1)
    toc = time.perf_counter()
    elapsed = toc - tic

    if verbose:
        duration = input.size(-1)/sr
        print(
            f"Processed {duration:0.2f} sec in {elapsed:0.3f} sec => {duration/elapsed:0.1f}x real-time")

    srcpath = os.path.dirname(inputfile)
    srcbasename = os.path.basename(inputfile).split(".")[0]

    outfile = os.path.join(out_path, srcbasename)

    # perform noise filtering
    if noise_reducer:
        model, df_state = model_dfn  # Load default model
        resampled = F.resample(out.cpu(), sr, 48000, lowpass_filter_width=6)
        enhanced_audio = enhance(model, df_state, resampled)

        save_audio(
            out_path+f"{srcbasename}-nr.wav", enhanced_audio, df_state.sr())

    else:
        # outfile += "-nr.wav"
        torchaudio.save(out_path+f"{srcbasename}-nr.wav", out.cpu(), sr)


def init_tcn_model(model_dir, model_id, gpu=False):

    checkpoint_path = glob.glob(os.path.join(model_dir,
                                             model_id,
                                             "lightning_logs",
                                             "version_0",
                                             "checkpoints",
                                             "*"))[0]

    hparams_file = os.path.join(model_dir, "hparams.yaml")
    batch_size = int(os.path.basename(model_id).split('-')[-1][2:])
    model_type = os.path.basename(model_id).split('-')[1]
    epoch = int(os.path.basename(checkpoint_path).split('-')[0].split('=')[-1])

    map_location = "cuda:0" if gpu else "cpu"

    if model_type == "LSTM":
        model = LSTMModel.load_from_checkpoint(
            checkpoint_path=checkpoint_path,
            map_location=map_location
        )

    else:
        model = TCNModel.load_from_checkpoint(
            checkpoint_path=checkpoint_path,
            map_location=map_location
        )
    return model


def init_dfn_model():
    model, df_state, _ = init_df()
    return model, df_state


def wav_nr_args(input_path, out_path, model_tcn, model_dfn, gpu=True, verbose=True):
    files = get_files(input_path)  # Get files or file from path
    for inputfile in files:
        tcn_dfn_process_args(inputfile, out_path, model_tcn,
                             model_dfn, gpu=gpu, verbose=verbose)  # norm 0.1 0.5


def tcn_dfn_process_buffer(audio, model_tcn,  sr=24000, limit=0.1, peak_red=0.5, gpu=False, verbose=True):
    input = torch.from_numpy(audio).unsqueeze(0)
    input = input.float() / 32768  # 32768
    # check if the input is mono
    if input.size(0) > 1:
        print(
            f"Warning: Model only supports mono audio, will downmix {input.size(0)} channels.")
        input = torch.sum(input, dim=0)

    # we will resample here if needed
    if sr != 44100:
        print(
            f"Warning: Model only operates at 44.1 kHz, will resample from {sr} Hz.")

    # construct conditioning
    params = torch.tensor([limit, peak_red])

    # add batch dimension
    input = input.view(1, 1, -1)
    params = params.view(1, 1, 2)

    # move to GPU
    if gpu:
        input = input.to("cuda:0")
        params = params.to("cuda:0")
        model_tcn.to("cuda:0")

    # pass through model
    tic = time.perf_counter()
    out = model_tcn(input, params).view(1, -1)
    toc = time.perf_counter()
    elapsed = toc - tic

    if verbose:
        duration = input.size(-1)/sr
        print(
            f"Processed {duration:0.2f} sec in {elapsed:0.3f} sec => {duration/elapsed:0.1f}x real-time")

    resampled = F.resample(out.cpu(), sr,
                           16000, lowpass_filter_width=6)

    return resampled.squeeze(0).detach().numpy()


def wav_nr_buffer(audio, model_tcn, gpu=True, verbose=True):
    # norm 0.1 0.5
    return tcn_dfn_process_buffer(audio, model_tcn, gpu=gpu, verbose=verbose)
