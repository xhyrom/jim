#!/bin/bash

MODEL_URL="https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin"

OUTPUT_PATH="ggml-base.bin"

curl -L -o $OUTPUT_PATH $MODEL_URL

echo "Model downloaded successfully to $OUTPUT_PATH"
