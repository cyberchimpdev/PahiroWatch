import json
import time
import ssl
import urllib.request
import certifi
from typing import Dict, Any, Optional, List
from backend.app.config import HACKATHON_KEY, OPENAI_API_BASE, MODEL_NAME

class HackathonLLMClient:
    """
    OpenAI-compatible client for the Startup Innovation Hackathon Vol. III
    Provided by Nexalaris Tech Pvt. Ltd. (Azure OpenAI endpoint)
    Supports single-turn completions and multi-turn ReAct conversations.
    """

    @staticmethod
    def is_configured() -> bool:
        return bool(HACKATHON_KEY and HACKATHON_KEY not in ["", "mock-or-live-key"])

    @staticmethod
    def chat(
        messages: List[Dict[str, str]],
        max_tokens: int = 350,
        temperature: float = 0.2,
        timeout: float = 25.0
    ) -> Dict[str, Any]:
        """
        Executes multi-turn chat completion against the Hackathon Azure OpenAI endpoint.
        """
        if not HackathonLLMClient.is_configured():
            return {
                "success": False,
                "content": "",
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
                "latency_ms": 0,
                "model": MODEL_NAME or "DeepSeek-V4-Flash",
                "error": "Hackathon API key not configured."
            }

        url = f"{OPENAI_API_BASE.rstrip('/')}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {HACKATHON_KEY}",
            "api-key": HACKATHON_KEY
        }

        payload = {
            "model": MODEL_NAME or "DeepSeek-V4-Flash",
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        start_time = time.time()
        try:
            data = json.dumps(payload).encode("utf-8")
            ctx = ssl.create_default_context(cafile=certifi.where())
            req = urllib.request.Request(url, data=data, headers=headers, method="POST")

            with urllib.request.urlopen(req, context=ctx, timeout=timeout) as resp:
                res_json = json.loads(resp.read().decode("utf-8"))
                latency_ms = int((time.time() - start_time) * 1000)

                content = res_json.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
                usage = res_json.get("usage", {})

                return {
                    "success": True,
                    "content": content,
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0),
                    "latency_ms": latency_ms,
                    "model": res_json.get("model", MODEL_NAME or "DeepSeek-V4-Flash"),
                    "error": None
                }
        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            return {
                "success": False,
                "content": "",
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
                "latency_ms": latency_ms,
                "model": MODEL_NAME or "DeepSeek-V4-Flash",
                "error": str(e)
            }

    @staticmethod
    def complete(
        prompt: str,
        system_prompt: str = "You are PahiroWatch, an autonomous landslide risk & emergency response agent for Nepal's Narayanghat-Mugling Highway (NH-05).",
        max_tokens: int = 250,
        temperature: float = 0.2
    ) -> Dict[str, Any]:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        return HackathonLLMClient.chat(messages, max_tokens=max_tokens, temperature=temperature)
