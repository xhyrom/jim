#[derive(Debug)]
pub struct SpeechToTextConfig {
    pub model_path: Option<String>,
    pub worker_url: Option<String>,
    pub api_key: Option<String>,
}
