from collections import deque

import numpy as np
import pyaudio
import webrtcvad

from .debug import time_me


class MicrophoneInput:
    chunk: int
    audio: pyaudio.PyAudio
    stream: pyaudio.Stream

    def __init__(self, chunk: int = 1280) -> None:
        self.chunk = chunk
        self.vad_chunk = 480  # 30ms

        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=self.chunk,
        )

        self.vad = webrtcvad.Vad(1)
        self.buffer = deque(maxlen=self.chunk * 2)

    def get_audio_frame(self):
        while True:
            frame = np.frombuffer(self.stream.read(self.chunk), dtype=np.int16)
            yield frame

    def _convert_chunks(self, data: np.ndarray, from_size: int, to_size: int) -> list:
        flat_data = data.flatten()
        n_chunks = len(flat_data) // to_size
        chunks = [flat_data[i * to_size : (i + 1) * to_size] for i in range(n_chunks)]

        remainder = flat_data[n_chunks * to_size :]
        if len(remainder) > 0:
            self.buffer.extend(remainder)

        if len(self.buffer) >= to_size:
            buffer_data = np.array(list(self.buffer)[:to_size])
            chunks.append(buffer_data)
            self.buffer = deque(list(self.buffer)[to_size:], maxlen=self.chunk * 2)

        return chunks

    @time_me
    def get_audio_vad(self, silence_duration=1):
        frames = []
        silent_frames = 0
        frames_to_be_silent = int(silence_duration * 16000 / self.chunk)
        is_speech_buffer = deque(maxlen=5)

        while True:
            frame = np.frombuffer(self.stream.read(self.chunk), dtype=np.int16)
            frames.append(frame)

            vad_chunks = self._convert_chunks(frame, self.chunk, self.vad_chunk)

            results = []
            for vad_chunk in vad_chunks:
                if len(vad_chunk) == self.vad_chunk:
                    is_speech = self.vad.is_speech(vad_chunk.tobytes(), 16000)
                    results.append(1 if is_speech else 0)

            if results:
                is_speech_buffer.append(sum(results) / len(results))

            if is_speech_buffer:
                speech_ratio = sum(is_speech_buffer) / len(is_speech_buffer)

                if speech_ratio < 0.3:
                    silent_frames += 1
                else:
                    silent_frames = 0

                if silent_frames >= frames_to_be_silent:
                    break

        return np.concatenate(frames)
