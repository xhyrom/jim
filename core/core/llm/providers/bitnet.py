from typing import Any, Dict, List

import aiohttp

from .base import LLMProvider, ProviderRegistry


@ProviderRegistry.register("bitnet")
class BitNetProvider(LLMProvider):
    def __init__(self, **kwargs):
        self.api_key = kwargs.get("api_key", "")
        self.model = kwargs.get("model", "microsoft/bitnet-b1.58-2B-4T")
        self.base_url = kwargs.get("base_url", "")
        self.local = kwargs.get("local", True)
        self.device = kwargs.get("device", "cuda" if self.local else None)
        self.use_hf = kwargs.get("use_hf", True)

        if self.use_hf and not self.local:
            self.base_url = (
                self.base_url or "https://api-inference.huggingface.co/models/"
            )
            if self.base_url.endswith("/"):
                self.base_url = self.base_url[:-1]

        self.loaded_model = None
        self.loaded_tokenizer = None

    async def _load_local_model(self):
        if self.loaded_model is None:
            try:
                import torch
                from transformers import AutoModelForCausalLM, AutoTokenizer

                print(f"Loading BitNet model {self.model} locally...")
                self.loaded_tokenizer = AutoTokenizer.from_pretrained(self.model)
                self.loaded_model = AutoModelForCausalLM.from_pretrained(
                    self.model,
                    torch_dtype=torch.float16
                    if self.device == "cuda"
                    else torch.float32,
                    device_map=self.device,
                )
                print(f"BitNet model loaded successfully on {self.device}")
            except Exception as e:
                print(f"Error loading BitNet model locally: {e}")
                raise

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 1024,
        temperature: float = 0.7,
        **kwargs,
    ) -> Dict[str, Any]:
        try:
            if self.local:
                return await self._generate_local(
                    messages, max_tokens, temperature, **kwargs
                )
            else:
                return await self._generate_api(
                    messages, max_tokens, temperature, **kwargs
                )
        except Exception as e:
            print(f"Error generating response from BitNet: {e}")
            return {
                "content": "I apologize, but I'm having trouble processing your request at the moment.",
                "finish_reason": "error",
                "model": self.model,
                "provider": "bitnet",
                "error": str(e),
            }

    async def _generate_local(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 1024,
        temperature: float = 0.7,
        **kwargs,
    ) -> Dict[str, Any]:
        try:
            import torch

            await self._load_local_model()

            formatted_prompt = self._format_chat_prompt(messages)

            inputs = self.loaded_tokenizer(formatted_prompt, return_tensors="pt").to(
                self.device
            )

            with torch.no_grad():
                generation_args = {
                    "max_new_tokens": max_tokens,
                    "temperature": temperature,
                    "top_p": 0.95,
                    "do_sample": temperature > 0,
                    "pad_token_id": self.loaded_tokenizer.eos_token_id,
                }

                outputs = self.loaded_model.generate(
                    inputs["input_ids"],
                    attention_mask=inputs.get("attention_mask", None),
                    **generation_args,
                )

            input_length = inputs["input_ids"].shape[1]
            generated_text = self.loaded_tokenizer.decode(
                outputs[0][input_length:], skip_special_tokens=True
            )

            return {
                "content": generated_text,
                "finish_reason": "stop",
                "model": self.model,
                "provider": "bitnet",
            }

        except Exception as e:
            print(f"Error generating response locally from BitNet: {e}")
            return {
                "content": "I apologize, but I'm having trouble processing your request locally.",
                "finish_reason": "error",
                "model": self.model,
                "provider": "bitnet",
                "error": str(e),
            }

    async def _generate_api(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 1024,
        temperature: float = 0.7,
        **kwargs,
    ) -> Dict[str, Any]:
        if self.use_hf and not self.api_key:
            raise ValueError(
                "HuggingFace API key required when using BitNet through HuggingFace API"
            )

        formatted_prompt = self._format_chat_prompt(messages)

        payload = {
            "inputs": formatted_prompt,
            "parameters": {
                "max_new_tokens": max_tokens,
                "temperature": temperature,
                "top_p": 0.95,
                "do_sample": True,
                "return_full_text": False,
            },
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/{self.model}"
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise ValueError(f"API error: {response.status} - {error_text}")

                data = await response.json()

                if isinstance(data, list) and len(data) > 0:
                    content = data[0].get("generated_text", "")
                else:
                    content = data.get("generated_text", "")

                return {
                    "content": content,
                    "finish_reason": "stop",
                    "model": self.model,
                    "provider": "bitnet",
                }

    def _format_chat_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Format messages for BitNet models, which might use a different chat template"""
        system_message = ""
        formatted_prompt = ""

        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
                break

        if system_message:
            formatted_prompt = f"<|im_start|>system\n{system_message}<|im_end|>\n"

        for msg in messages:
            if msg["role"] == "system":
                continue  # Already handled
            elif msg["role"] == "user":
                formatted_prompt += f"<|im_start|>user\n{msg['content']}<|im_end|>\n"
            elif msg["role"] == "assistant":
                formatted_prompt += (
                    f"<|im_start|>assistant\n{msg['content']}<|im_end|>\n"
                )

        formatted_prompt += "<|im_start|>assistant\n"

        return formatted_prompt
