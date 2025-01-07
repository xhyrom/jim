#!/bin/bash

# Define the URL of the model
MODEL_URL="https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin"

# Define the output path
OUTPUT_PATH="ggml-base.bin"

# Download the model using curl
curl -L -o $OUTPUT_PATH $MODEL_URL

# Print a success message
echo "Model downloaded successfully to $OUTPUT_PATH"
