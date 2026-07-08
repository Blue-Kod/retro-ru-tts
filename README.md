# retro-ru-tts

[Читать на русском](README_RU.md)

Python wrapper for the [ru_tts](https://github.com/poretsky/ru_tts) speech
synthesizer — a compact, portable Russian TTS engine written in pure C.

The core is a reverse-engineered reimplementation of the SDRV resident speech
driver (BelSInt lab, Institute of Technical Cybernetics, Academy of Sciences of
the Byelorussian SSR, 1990). It uses formant (diphone) synthesis: no ML models,
no GPU, no large dependencies — just simple, fast, deterministic speech
generation.

## Quick start

```bash
pip install retro-ru-tts
```

```python
import retro_ru_tts

# Synthesize and play through speakers
retro_ru_tts.synthesize("Привет, мир!")

# Get raw PCM data without playing
pcm = retro_ru_tts.synthesize("Привет", play=False)

# Save to WAV file
wav = retro_ru_tts.pcm_to_wav(pcm)
with open("output.wav", "wb") as f:
    f.write(wav)
```

## API

### `synthesize(text, ...)`

```python
retro_ru_tts.synthesize(
    "Привет, мир!",

    # Voice parameters
    speech_rate=100,     # speech rate (20–500)
    voice_pitch=100,     # voice pitch (50–300)
    intonation=100,      # expressiveness (0–140)

    # Gap factors (pause duration between clauses, default 100)
    general_gap_factor=100,
    comma_gap_factor=100,
    dot_gap_factor=100,
    semicolon_gap_factor=100,
    colon_gap_factor=100,
    question_gap_factor=100,
    exclamation_gap_factor=100,
    intonational_gap_factor=100,

    # Control flags (bitmask)
    flags=3,             # default: DEC_SEP_POINT | DEC_SEP_COMMA

    # Behaviour
    wave_buffer_size=8192,  # internal buffer (256–1048576)
    play=True,              # play through speakers
    normalize=True,         # text normalization (see below)
)
```

**Returns:** `bytes` — raw signed 8-bit PCM audio at 10 kHz, mono.

### `play(text, ...)`

Shortcut for `synthesize(text, play=True)`. Same parameters (except `play`).

### `pcm_to_wav(pcm_bytes)`

Wraps raw signed 8-bit PCM into a WAV container.

**Returns:** `bytes` — complete WAV file (8-bit, 10 kHz, mono).

## Flags

The `flags` parameter is a bitmask controlling decimal separation and voice:

| Flag | Value | Description |
|---|---|---|
| `DEC_SEP_POINT` | 1 | Treat `.` as decimal separator (e.g., `3.14`) |
| `DEC_SEP_COMMA` | 2 | Treat `,` as decimal separator (e.g., `3,14`) |
| `USE_ALTERNATIVE_VOICE` | 4 | Use alternative (female) voice |
| `USE_LEGACY_RATE_ALGO` | 8 | Use legacy linear interpolation rate algorithm instead of adaptive crossfade |

Default value is `3` (`DEC_SEP_POINT \| DEC_SEP_COMMA`), which means both `.` and `,` are accepted as decimal separators.

To use the female voice without decimal comma: `flags=5` (`DEC_SEP_POINT \| USE_ALTERNATIVE_VOICE`).

## Text normalization

By default the input text is normalized via
[ru-normalizr](https://pypi.org/project/ru-normalizr/) in TTS mode before being
fed to the synthesizer. This converts numbers to words, formats dates, handles
cases, transliterates English words, etc.

```python
# Skip normalization for raw KOI8-R PCM output
retro_ru_tts.synthesize("Версия 3.2", normalize=False)
```

## PCM format

| Property | Value |
|---|---|
| Format | Signed 8-bit PCM |
| Sample rate | 10000 Hz |
| Channels | Mono (1) |

## Build from source

### Prerequisites

- C compiler (GCC, Clang, MSVC)
- Python 3.7+ with setuptools
- Make (Linux) or build tools (Windows)

### Steps

```bash
git clone https://github.com/your/repo.git
cd retro-ru-tts

# Development install (editable)
pip install -e .

# Build distribution package
pip install build
python -m build
```

## PCM output data

The engine produces raw signed 8-bit PCM at a fixed 10 kHz sample rate, mono.
This is a deliberately minimal, low-bandwidth format suitable for embedded
systems, screen readers, and retro computing applications.

## License

MIT. This wrapper is distributed under the same license as the original
[ru_tts](https://github.com/poretsky/ru_tts) by Igor Poretsky. See LICENSE
for details.
