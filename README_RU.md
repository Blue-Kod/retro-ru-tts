# retro-ru-tts

[Read in English](README.md)

Python-обёртка для [ru_tts](https://github.com/poretsky/ru_tts) —
компактный русский речевой синтезатор на чистом C.

В основе — реверс-инжиниринг SDRV-драйвера (лаборатория BelSInt, институт
технической кибернетики АН БССР, 1990). Формантный (дифонный) синтез:
никаких ML-моделей, GPU или тяжёлых зависимостей — просто, быстро,
детерминированно.

## Быстрый старт

```bash
pip install retro-ru-tts
```

```python
import retro_ru_tts

# Синтез и воспроизведение
retro_ru_tts.synthesize("Привет, мир!")

# Только PCM (без звука)
pcm = retro_ru_tts.synthesize("Привет", play=False)

# Сохранить в WAV
wav = retro_ru_tts.pcm_to_wav(pcm)
with open("output.wav", "wb") as f:
    f.write(wav)
```

## API

### `synthesize(text, ...)`

```python
retro_ru_tts.synthesize(
    "Привет, мир!",

    # Параметры голоса
    speech_rate=100,     # темп речи (20–500)
    voice_pitch=100,     # высота голоса (50–300)
    intonation=100,      # выразительность (0–140)

    # Паузы между фрагментами (по умолчанию 100)
    general_gap_factor=100,
    comma_gap_factor=100,
    dot_gap_factor=100,
    semicolon_gap_factor=100,
    colon_gap_factor=100,
    question_gap_factor=100,
    exclamation_gap_factor=100,
    intonational_gap_factor=100,

    # Флаги (битовая маска)
    flags=3,             # по умолчанию: DEC_SEP_POINT | DEC_SEP_COMMA

    # Поведение
    wave_buffer_size=8192,  # внутренний буфер (256–1048576)
    play=True,              # воспроизвести через динамики
    normalize=True,         # нормализация текста (см. ниже)
)
```

**Возвращает:** `bytes` — raw signed 8-bit PCM, 10 кГц, моно.

### `play(text, ...)`

Сокращение для `synthesize(text, play=True)`. Те же параметры (кроме `play`).

### `pcm_to_wav(pcm_bytes)`

Упаковывает raw PCM в WAV-контейнер.

**Возвращает:** `bytes` — готовый WAV-файл (8-bit, 10 кГц, моно).

## Флаги

Параметр `flags` — битовая маска, управляющая разделителями и голосом:

| Флаг | Значение | Описание |
|---|---|---|
| `DEC_SEP_POINT` | 1 | Использовать `.` как десятичный разделитель (например, `3.14`) |
| `DEC_SEP_COMMA` | 2 | Использовать `,` как десятичный разделитель (например, `3,14`) |
| `USE_ALTERNATIVE_VOICE` | 4 | Использовать альтернативный (женский) голос |
| `USE_LEGACY_RATE_ALGO` | 8 | Использовать старый алгоритм изменения темпа (линейная интерполяция) вместо адаптивного кроссфейда |

По умолчанию `3` (`DEC_SEP_POINT | DEC_SEP_COMMA`) — принимаются оба
разделителя. Для женского голоса без десятичной запятой: `flags=5`.

## Нормализация текста

По умолчанию текст нормализуется через
[ru-normalizr](https://pypi.org/project/ru-normalizr/) в TTS-режиме:
числа → слова, даты, падежи, транслитерация английских слов и т.д.

```python
# Без нормализации (сырой PCM)
retro_ru_tts.synthesize("Версия 3.2", normalize=False)
```

## Формат PCM

| Параметр | Значение |
|---|---|
| Формат | Signed 8-bit PCM |
| Частота дискретизации | 10000 Гц |
| Каналы | Моно |

## Сборка из исходников

### Требования

- Компилятор C (GCC, Clang, MSVC)
- Python 3.7+ с setuptools
- Make (Linux) или инструменты сборки (Windows)

### Шаги

```bash
git clone https://github.com/Blue-Kod/retro-ru-tts.git
cd retro-ru-tts

# Разработка (editable install)
pip install -e .

# Сборка дистрибутива
pip install build
python -m build
```

## Лицензия

MIT. Обёртка распространяется под той же лицензией, что и оригинальный
[ru_tts](https://github.com/poretsky/ru_tts) Игоря Порецкого. См. LICENSE.
