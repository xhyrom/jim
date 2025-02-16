from time import perf_counter

from faster_whisper import WhisperModel


class WhisperService:
    model: WhisperModel

    def __init__(self, model_path: str):
        self.model = WhisperModel(
            model_size_or_path=model_path, device="cpu", compute_type="int8"
        )

    def run(self):
        segments, info = self.model.transcribe(
            "../eng.wav", beam_size=5, language="en", condition_on_previous_text=False
        )

        t1 = perf_counter()
        for segment in segments:
            print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
        t2 = perf_counter()
        print("Transcription took %.2fs" % (t2 - t1))
