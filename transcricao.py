import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import threading
import time
import speech_recognition as sr
import io

class transcrever_audio:
    def __init__(self, callback_texto, timeout=8, sample_rate=16000, duracao=4):
        self.sample_rate = sample_rate
        self.duracao = duracao
        self.callback_texto = callback_texto
        self._timeout = timeout
        self._ultimo_texto = time.time()
        self._thread = None
        self._verificador_thread = None
        self._executando = False

    def _gravar_audio(self):
        while self._executando:
            audio = sd.rec(int(self.duracao * self.sample_rate), samplerate=self.sample_rate, channels=1, dtype='int16')
            sd.wait()

            buffer = io.BytesIO()
            wav.write(buffer, self.sample_rate, audio)
            buffer.seek(0)

            try:
                reconhecedor = sr.Recognizer()
                with sr.AudioFile(buffer) as fonte:
                    audio_data = reconhecedor.record(fonte)
                    texto = reconhecedor.recognize_google(audio_data, language='pt-BR')
                    self._ultimo_texto = time.time()
                    self.callback_texto(texto)
            except sr.UnknownValueError:
                self.callback_texto("[Ininteligível]")
            except sr.RequestError as e:
                self.callback_texto(f"[Erro]: {e}")

    def iniciar(self):
        self._executando = True
        self._ultimo_texto = time.time()

        self._thread = threading.Thread(target=self._gravar_audio)
        self._thread.daemon = True
        self._thread.start()

        self._verificador_thread = threading.Thread(target=self._verificar_silencio)
        self._verificador_thread.daemon = True
        self._verificador_thread.start()

    def _verificar_silencio(self):
        while self._executando:
            if time.time() - self._ultimo_texto > self._timeout:
                self.callback_texto("[Pausado por inatividade]")
                self.parar()
                break
            time.sleep(2)

    def parar(self):
        self._executando = False
