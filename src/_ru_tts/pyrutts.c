#include <Python.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#include "ru_tts.h"
#include "sink.h"
#include "synth.h"

typedef struct {
    PyObject *bytes_list;
    size_t total_size;
} collect_t;

static int wave_callback(void *buffer, size_t size, void *user_data) {
    collect_t *collect = (collect_t *)user_data;
    PyObject *chunk = PyBytes_FromStringAndSize((const char *)buffer, size);
    if (!chunk) {
        collect->total_size = (size_t)-1;
        return 1;
    }
    if (PyList_Append(collect->bytes_list, chunk) < 0) {
        Py_DECREF(chunk);
        collect->total_size = (size_t)-1;
        return 1;
    }
    collect->total_size += size;
    Py_DECREF(chunk);
    return 0;
}

static PyObject *py_ru_tts_synthesize(PyObject *self, PyObject *args, PyObject *kwargs) {
    const char *text;
    Py_ssize_t text_len;
    ru_tts_conf_t config;
    ru_tts_config_init(&config);
    int wave_buf_size = 8192;

    static char *kwlist[] = {
        "text",
        "speech_rate",
        "voice_pitch",
        "intonation",
        "general_gap_factor",
        "comma_gap_factor",
        "dot_gap_factor",
        "semicolon_gap_factor",
        "colon_gap_factor",
        "question_gap_factor",
        "exclamation_gap_factor",
        "intonational_gap_factor",
        "flags",
        "wave_buffer_size",
        NULL
    };

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "y#|iiiiiiiiiiiii", kwlist,
                                     &text, &text_len,
                                     &config.speech_rate,
                                     &config.voice_pitch,
                                     &config.intonation,
                                     &config.general_gap_factor,
                                     &config.comma_gap_factor,
                                     &config.dot_gap_factor,
                                     &config.semicolon_gap_factor,
                                     &config.colon_gap_factor,
                                     &config.question_gap_factor,
                                     &config.exclamation_gap_factor,
                                     &config.intonational_gap_factor,
                                     &config.flags,
                                     &wave_buf_size)) {
        return NULL;
    }

    if (wave_buf_size < 256) wave_buf_size = 256;
    if (wave_buf_size > 1048576) wave_buf_size = 1048576;

    char *wave_buffer = (char *)malloc(wave_buf_size);
    if (!wave_buffer) {
        PyErr_NoMemory();
        return NULL;
    }

    collect_t collect;
    collect.bytes_list = PyList_New(0);
    collect.total_size = 0;
    if (!collect.bytes_list) {
        free(wave_buffer);
        return NULL;
    }

    ru_tts_transfer(&config, text, wave_buffer, wave_buf_size, wave_callback, &collect);

    if (collect.total_size == (size_t)-1) {
        Py_DECREF(collect.bytes_list);
        free(wave_buffer);
        if (!PyErr_Occurred())
            PyErr_SetString(PyExc_RuntimeError, "synthesis failed");
        return NULL;
    }

    PyObject *result = PyBytes_FromStringAndSize(NULL, (Py_ssize_t)collect.total_size);
    if (!result) {
        Py_DECREF(collect.bytes_list);
        free(wave_buffer);
        return NULL;
    }

    char *dst = PyBytes_AS_STRING(result);
    Py_ssize_t offset = 0;
    for (Py_ssize_t i = 0; i < PyList_Size(collect.bytes_list); i++) {
        PyObject *chunk = PyList_GET_ITEM(collect.bytes_list, i);
        Py_ssize_t chunk_size;
        const char *chunk_data;
        if (PyBytes_AsStringAndSize(chunk, (char **)&chunk_data, &chunk_size) < 0) {
            Py_DECREF(result);
            Py_DECREF(collect.bytes_list);
            free(wave_buffer);
            return NULL;
        }
        memcpy(dst + offset, chunk_data, chunk_size);
        offset += chunk_size;
    }

    Py_DECREF(collect.bytes_list);
    free(wave_buffer);
    return result;
}

static PyMethodDef RuTtsMethods[] = {
    {"synthesize", (PyCFunction)py_ru_tts_synthesize, METH_VARARGS | METH_KEYWORDS,
     "Synthesize speech from koi8-r encoded text.\n\n"
     "Args:\n"
     "    text: bytes in koi8-r encoding\n"
     "    speech_rate: speech rate (20-500, default 100)\n"
     "    voice_pitch: voice pitch (50-300, default 100)\n"
     "    intonation: intonation level (0-140, default 100)\n"
     "    general_gap_factor: gap factor (default 100)\n"
     "    comma_gap_factor: comma gap (default 100)\n"
     "    dot_gap_factor: dot gap (default 100)\n"
     "    semicolon_gap_factor: semicolon gap (default 100)\n"
     "    colon_gap_factor: colon gap (default 100)\n"
     "    question_gap_factor: question gap (default 100)\n"
     "    exclamation_gap_factor: exclamation gap (default 100)\n"
     "    intonational_gap_factor: intonational gap (default 100)\n"
     "    flags: TTS control flags (default DEC_SEP_POINT|DEC_SEP_COMMA=3)\n"
     "    wave_buffer_size: internal buffer size (256-1048576, default 8192)\n\n"
     "Returns:\n"
     "    bytes: raw signed 8-bit PCM audio at 10 kHz, mono\n"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef ru_tts_native_module = {
    PyModuleDef_HEAD_INIT,
    "_ru_tts_native",
    NULL,
    -1,
    RuTtsMethods
};

PyMODINIT_FUNC PyInit__ru_tts_native(void) {
    return PyModule_Create(&ru_tts_native_module);
}
