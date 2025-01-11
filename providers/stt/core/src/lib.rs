use async_trait::async_trait;
use thiserror::Error;

#[derive(Error, Debug)]
pub enum TranscriberError {
    #[error("Invalid audio data")]
    InvalidAudioData,

    #[error("Unknown error: {0}")]
    Unknown(String),
}

#[async_trait]
pub trait TranscriberProvider {
    async fn transcribe(&self, audio_data: Vec<u8>) -> Result<String, TranscriberError>;
}
