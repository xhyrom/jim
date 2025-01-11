use std::{io::Cursor, sync::Arc};

use anyhow::Result;
use async_trait::async_trait;
use hound::WavReader;
use stt_core::{TranscriberError, TranscriberProvider};
use whisper_rs::{
    FullParams, SamplingStrategy, WhisperContext, WhisperContextParameters, WhisperError,
};

pub struct WhisperProvider {
    context: Arc<WhisperContext>,
}

impl WhisperProvider {
    pub fn new(model_path: &str) -> Self {
        let params = WhisperContextParameters::default();
        let context = Arc::new(
            WhisperContext::new_with_params(&model_path, params)
                .expect("Failed to create WhisperContext"),
        );

        Self { context }
    }
}

pub struct WhisperProviderError(pub WhisperError);

impl From<WhisperProviderError> for TranscriberError {
    fn from(err: WhisperProviderError) -> Self {
        TranscriberError::Whisper(err.0.to_string())
    }
}

#[async_trait]
impl TranscriberProvider for WhisperProvider {
    async fn transcribe(&self, audio_data: Vec<u8>) -> Result<String, TranscriberError> {
        if audio_data.is_empty() {
            return Err(TranscriberError::InvalidAudioData);
        }

        let cursor = Cursor::new(audio_data);
        let samples: Vec<i16> = WavReader::new(cursor)
            .map_err(|_| TranscriberError::InvalidAudioData)?
            .into_samples::<i16>()
            .map(|s| s.unwrap())
            .collect();

        let mut params = FullParams::new(SamplingStrategy::Greedy { best_of: 1 });

        params.set_language(Some("sk"));
        params.set_print_special(false);
        params.set_print_progress(false);
        params.set_print_realtime(false);
        params.set_print_timestamps(false);

        let mut inter_samples = vec![Default::default(); samples.len()];
        whisper_rs::convert_integer_to_float_audio(&samples, &mut inter_samples)
            .expect("failed to convert audio data");

        let samples = whisper_rs::convert_stereo_to_mono_audio(&inter_samples)
            .expect("failed to convert audio data");

        let mut state = self.context.create_state().map_err(WhisperProviderError)?;
        state
            .full(params, &samples[..])
            .map_err(WhisperProviderError)?;

        let mut result = String::new();

        for segment in 0..state.full_n_segments().map_err(WhisperProviderError)? {
            result.push_str(
                &state
                    .full_get_segment_text(segment)
                    .map_err(WhisperProviderError)?,
            );
            result.push_str(" ");
        }

        Ok(result)
    }
}
