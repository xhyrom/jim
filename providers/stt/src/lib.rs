pub use stt_core::*;
pub mod config;

pub fn create_provider(config: &config::SpeechToTextConfig) -> Box<dyn TranscriberProvider> {
    #[cfg(feature = "local")]
    {
        return Box::new(stt_local::WhisperProvider::new(
            config
                .model_path
                .as_ref()
                .expect("model_path required for local provider"),
        ));
    }

    #[cfg(feature = "cloudflare")]
    {
        return Box::new(stt_cloudflare::CloudflareSTT::new(
            config
                .worker_url
                .as_ref()
                .expect("worker_url required for cloudflare provider"),
        ));
    }
}
