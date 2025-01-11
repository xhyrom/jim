use anyhow::Result;
use async_trait::async_trait;
use stt_core::{TranscriberError, TranscriberProvider};

pub struct WhisperProvider {
    model_path: String,
}

impl WhisperProvider {
    pub fn new(model_path: &str) -> Self {
        Self {
            model_path: model_path.to_string(),
        }
    }
}

#[async_trait]
impl TranscriberProvider for WhisperProvider {
    async fn transcribe(&self, audio_data: Vec<u8>) -> Result<String, TranscriberError> {
        if audio_data.is_empty() {
            return Err(TranscriberError::InvalidAudioData);
        }

        todo!("Implement Whisper transcription")
    }
}
