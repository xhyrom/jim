use anyhow::Result;
use async_trait::async_trait;
use stt_core::{TranscriberError, TranscriberProvider};

pub struct CloudflareTranscriber {
    worker_url: String,
}

impl CloudflareTranscriber {
    pub fn new(worker_url: &str) -> Self {
        Self {
            worker_url: worker_url.to_string(),
        }
    }
}

#[async_trait]
impl TranscriberProvider for CloudflareTranscriber {
    async fn transcribe(&self, audio_data: Vec<u8>) -> Result<String, TranscriberError> {
        if audio_data.is_empty() {
            return Err(TranscriberError::InvalidAudioData);
        }

        // Implement Cloudflare Workers transcription
        todo!("Implement Cloudflare transcription")
    }
}
