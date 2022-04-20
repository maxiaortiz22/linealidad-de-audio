"""
La idea es abrir el micrófono y captar en 16 bits hasta que supero un treshold de silencio. Una vez detectado
que no hay silencio, corto ese stream y arranco otro a 24 bits con la duración de la prueba en cuestión. La razón
por la cual lo hago así es porque es intuitivo para mi realizar el treshold a 16 bits y no a 24. En el futuro
preguntarle a mati si sabe ajustar el treshold en 24.0

Saco lo de silencio de GrabarAudioRecortarSilencio.py y la grabación a 24 bits de:
https://stackoverflow.com/questions/23370556/recording-24-bit-audio-with-pyaudio

Al final tengo que usar 32bit float y no 24 así que tuve que mudarme a sounddevice para grabar y a librosa
para guardar el audio!!!
"""

from sys import byteorder
from array import array
from struct import pack

import pyaudio
import wave
import sounddevice as sd
from scipy.io.wavfile import write

#Detector de sonido en 16 bits:
THRESHOLD = 100 #500 el original
CHUNK_SIZE_silence = 1024
FORMAT_silence = pyaudio.paInt16
RATE_silence = 44100

#Grabación en 32 bits flotantes:
CHANNELS = 1
RATE = 44100
#RECORD_SECONDS = 5
#WAVE_OUTPUT_FILENAME = "veo_si_sirve.wav"


def is_silent(snd_data):
    "Returns 'True' if below the 'silent' threshold"
    return max(snd_data) < THRESHOLD


def record(RECORD_SECONDS, sr=44100):
    """
    Detect when a signal appears and start recording
    """
    p_silence = pyaudio.PyAudio()
    stream = p_silence.open(format=FORMAT_silence, channels=1, rate=RATE_silence,
        input=True, output=True,
        frames_per_buffer=CHUNK_SIZE_silence)

    r_silence = array('h')

    while 1:
        # little endian, signed short
        snd_data = array('h', stream.read(CHUNK_SIZE_silence))
        if byteorder == 'big':
            snd_data.byteswap()
        r_silence.extend(snd_data)

        silent = is_silent(snd_data)

        if silent == False:
            break #Mato el loop cuando paso el umbral

    
    #sample_width_silence = p_silence.get_sample_size(FORMAT_silence)
    stream.stop_stream()
    stream.close()
    p_silence.terminate()

    print('Señal detectada! Comienza grabación')

    myrecording = sd.rec(int(RECORD_SECONDS * sr), samplerate=sr,
                     channels=CHANNELS, blocking=True, dtype='float32')

    write('test_JBL750.wav', RATE, myrecording)
    return myrecording, sr


"""
if __name__ == '__main__':
    print("Envíar sonido")
    record()
    print(f"Listo, resultado escrito en {WAVE_OUTPUT_FILENAME}")
"""
