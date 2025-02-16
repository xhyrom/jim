from pathlib import Path

import numpy as np
import pyaudio
from openwakeword.model import Model


class WakeService:
    model: Model
    threshold: float
    chunk: int
    audio: pyaudio.PyAudio
    stream: pyaudio.Stream

    def __init__(self, model_paths: list[Path], threshold=0.5):
        self.model = Model([str(model_path) for model_path in model_paths])
        self.threshold = threshold

        self.chunk = 1280

        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=self.chunk,
        )

    def get_audio_frame(self):
        while True:
            frame = np.frombuffer(self.stream.read(self.chunk), dtype=np.int16)
            yield frame

    def run(self):
        for frame in self.get_audio_frame():
            predictions: dict[str, float] = self.model.predict(frame)  # type: ignore

            for model_name, prediction in predictions.items():
                if prediction > self.threshold:
                    return f"{model_name} {prediction}"

        return None
