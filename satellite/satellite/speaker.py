import numpy as np
import pyaudio


class SpeakerOutput:
    chunk: int
    audio: pyaudio.PyAudio
    stream: pyaudio.Stream

    def __init__(self, chunk: int = 2048, rate: int = 22050) -> None:
        self.chunk = chunk

        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=rate,
            output=True,
            frames_per_buffer=self.chunk,
        )

    def play_audio(self, audio_data: np.ndarray | bytes) -> None:
        if isinstance(audio_data, bytes):
            audio_data = np.frombuffer(audio_data, dtype=np.int16)

        audio_data = audio_data.astype(np.int16)

        for i in range(0, len(audio_data), self.chunk):
            chunk = audio_data[i : i + self.chunk]
            if len(chunk) < self.chunk:
                chunk = np.pad(chunk, (0, self.chunk - len(chunk)))

            self.stream.write(chunk.tobytes())
