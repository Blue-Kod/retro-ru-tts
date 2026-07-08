"""ru_tts - Russian text-to-speech synthesis.

Pure C library wrapped for Python. Produces raw signed 8-bit PCM at 10 kHz.

Usage:
    import ru_tts
    ru_tts.synthesize("Привет, мир!")   # plays through speakers
    pcm = ru_tts.synthesize("Привет", play=False)  # returns bytes only
"""

import struct
import io
from _ru_tts_native import synthesize as _synthesize_native

__all__ = ["synthesize", "play", "pcm_to_wav"]


def _pcm_to_wav(pcm_bytes):
    sample_rate = 10000
    data_size = len(pcm_bytes)
    unsigned = bytes((b + 128) & 0xFF for b in pcm_bytes)
    buf = io.BytesIO()
    buf.write(b'RIFF')
    buf.write(struct.pack('<I', 36 + data_size))
    buf.write(b'WAVE')
    buf.write(b'fmt ')
    buf.write(struct.pack('<I', 16))
    buf.write(struct.pack('<H', 1))
    buf.write(struct.pack('<H', 1))
    buf.write(struct.pack('<I', sample_rate))
    buf.write(struct.pack('<I', sample_rate))
    buf.write(struct.pack('<H', 1))
    buf.write(struct.pack('<H', 8))
    buf.write(b'data')
    buf.write(struct.pack('<I', data_size))
    buf.write(unsigned)
    return buf.getvalue()


def _play_pcm(pcm_bytes):
    wav = _pcm_to_wav(pcm_bytes)
    try:
        import winsound
        winsound.PlaySound(wav, winsound.SND_MEMORY)
    except ImportError:
        import platform
        if platform.system() == "Linux":
            import subprocess, tempfile, os
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                f.write(wav)
                tmppath = f.name
            try:
                subprocess.run(["aplay", tmppath], check=True)
            except FileNotFoundError:
                subprocess.run(["paplay", tmppath], check=True)
            finally:
                os.unlink(tmppath)
        else:
            raise RuntimeError("Audio playback not supported on this platform")


def _normalize_text(text):
    try:
        from ru_normalizr import NormalizeOptions, Normalizer
        _norm = Normalizer(NormalizeOptions.tts())
        return _norm.normalize(text)
    except ImportError:
        pass
    return text.replace("\u0301", "").replace("+", "").strip()


def synthesize(text, speech_rate=100, voice_pitch=100, intonation=100,
               general_gap_factor=100, comma_gap_factor=100,
               dot_gap_factor=100, semicolon_gap_factor=100,
               colon_gap_factor=100, question_gap_factor=100,
               exclamation_gap_factor=100, intonational_gap_factor=100,
               flags=3, wave_buffer_size=8192, play=True, normalize=True):
    """Synthesize speech from a Russian text string.

    Args:
        text: str or bytes (koi8-r) - Russian text to synthesize
        speech_rate: speech rate (20-500, default 100)
        voice_pitch: voice pitch (50-300, default 100)
        intonation: intonation level (0-140, default 100)
        general_gap_factor: gap between clauses (default 100)
        comma_gap_factor: pause after comma (default 100)
        dot_gap_factor: pause after dot (default 100)
        semicolon_gap_factor: pause after semicolon (default 100)
        colon_gap_factor: pause after colon (default 100)
        question_gap_factor: pause after question mark (default 100)
        exclamation_gap_factor: pause after exclamation mark (default 100)
        intonational_gap_factor: intonational pause (default 100)
        flags: bitmask of DEC_SEP_POINT (1), DEC_SEP_COMMA (2),
               USE_ALTERNATIVE_VOICE (4) (default 3 = both separators)
        wave_buffer_size: internal buffer size (default 8192)
        play: if True, play audio through speakers (default True)
        normalize: if True, normalize text via ru-normalizr if installed

    Returns:
        bytes: raw signed 8-bit PCM audio at 10 kHz, mono
    """
    if isinstance(text, str):
        if normalize:
            text = _normalize_text(text)
        text = text.replace("\u0301", "+").encode("koi8-r", errors="replace")
    elif not isinstance(text, bytes):
        raise TypeError("text must be str or bytes")

    pcm = _synthesize_native(
        text,
        speech_rate=speech_rate,
        voice_pitch=voice_pitch,
        intonation=intonation,
        general_gap_factor=general_gap_factor,
        comma_gap_factor=comma_gap_factor,
        dot_gap_factor=dot_gap_factor,
        semicolon_gap_factor=semicolon_gap_factor,
        colon_gap_factor=colon_gap_factor,
        question_gap_factor=question_gap_factor,
        exclamation_gap_factor=exclamation_gap_factor,
        intonational_gap_factor=intonational_gap_factor,
        flags=flags,
        wave_buffer_size=wave_buffer_size,
    )

    if play:
        _play_pcm(pcm)

    return pcm


def play(text, speech_rate=100, voice_pitch=100, intonation=100,
         flags=3, wave_buffer_size=8192):
    """Synthesize and play speech through speakers (convenience wrapper)."""
    return synthesize(
        text,
        speech_rate=speech_rate,
        voice_pitch=voice_pitch,
        intonation=intonation,
        flags=flags,
        wave_buffer_size=wave_buffer_size,
        play=True,
    )


def pcm_to_wav(pcm_bytes):
    """Wrap raw signed 8-bit PCM bytes into a WAV file bytes."""
    return _pcm_to_wav(pcm_bytes)
