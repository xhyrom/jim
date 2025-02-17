from pathlib import Path

from openwakeword.model import Model

from .microphone import MicrophoneInput


class WakeService:
    model: Model
    threshold: float

    def __init__(self, model_paths: list[Path], threshold=0.5):
        self.model = Model([str(model_path) for model_path in model_paths])
        self.threshold = threshold

    def run(self, microphone: MicrophoneInput) -> bool:
        self.model.reset()

        for frame in microphone.get_audio_frame():
            predictions: dict[str, float] = self.model.predict(frame)  # type: ignore

            for model_name, prediction in predictions.items():
                if prediction > self.threshold:
                    print(f"{model_name} {prediction}")
                    return True

        return False
