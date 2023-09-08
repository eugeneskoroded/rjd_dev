import numpy as np
import whisperx
import os
import subprocess
import ffmpeg


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


def load_audio(file: (str, bytes), sr: int = 16000):
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

    return np.frombuffer(out, np.int16).flatten().astype(np.float32) / 32768.0


def init_asr_model(model_name, device, language="ru", compute_type='float16', asr_opt=None):
    model = whisperx.load_model(whisper_arch=model_name, device=device, compute_type=compute_type,
                                download_root='./models/', asr_options=asr_opt, language=language)
    return model


def asr_model_transcribe(asr_model, audio_file, batch_size=32):
    # audio_ = load_audio(audio_file)
    result = asr_model.transcribe(audio=audio_file, batch_size=batch_size)
    # result['audio'] = str(audio_file)
    return result
