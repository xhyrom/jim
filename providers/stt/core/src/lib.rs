use async_trait::async_trait;
use thiserror::Error;

#[derive(Error, Debug)]
pub enum TranscriberError {
    #[error("IO: {0}")]
    Io(#[from] std::io::Error),

    #[error("Invalid audio data")]
    InvalidAudioData,

    #[error("Unknown error: {0}")]
    Unknown(String),

    #[error("Wishper error: {0}")]
    Whisper(String),

    #[error(transparent)]
    Provider(#[from] anyhow::Error),
}

#[async_trait]
pub trait TranscriberProvider: Send + Sync {
    async fn transcribe(&self, audio_data: Vec<u8>) -> Result<String, TranscriberError>;
}
