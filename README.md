# retro-ru-tts

[Читать на русском](README_RU.md) | [GitHub](https://github.com/Blue-Kod/retro-ru-tts)

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

# Optional: ru-normalizr for advanced normalization (Python ≥ 3.10)
pip install retro-ru-tts[normalize]
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

By default the input text is normalized before being fed to the synthesizer.
This converts numbers to words, formats dates and times, expands abbreviations,
spells out uppercase acronyms letter by letter, transliterates common English
words, and cleans up punctuation.

If [ru-normalizr](https://pypi.org/project/ru-normalizr/) is installed
(`pip install retro-ru-tts[normalize]`), it is used for normalization.
Otherwise, a built-in normalizer handles the most common cases:

| Feature | Example | Output |
|---|---|---|
| Stress marks | ко́фе | кофе |
| Numbers | 1234567 | один миллион двести тридцать четыре тысячи пятьсот шестьдесят семь |
| Dates | 15.03.2024 | пятнадцатое марта две тысячи двадцать четыре года |
| Time | 14:30 | четырнадцать тридцать |
| Units | 5 кг, 100 мл | пять килограмм, сто миллилитров |
| Temperature | -5 °C | минус пять градусов по Цельсию |
| Currency | 300 руб., 50$ | триста рублей, пятьдесят долларов |
| Symbols | 100%, №5 | сто процентов, номер пять |
| Abbreviations | т.д., т.е., напр. | так далее, то есть, например |
| Acronyms | TTS, РФ, USB | тэ тэ эс, эр эф, у эс бэ |
| Ordinals | 1-й, 3-я | первый, третья |
| Decimals | 3.14 | три запятая одна четыре |
| Phone | +7 495 123 45 67 | восемь четыре девять пять один два три четыре пять шесть семь |
| English | hello, world, ok | хэллоу, уорлд, окей |
| URLs | example.com/privet | эксэмпэл точка ком слэш привет |
| Emails | user@example.com | электронный адрес |

```python
# Skip normalization for raw PCM output
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
git clone https://github.com/Blue-Kod/retro-ru-tts.git
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
