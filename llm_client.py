import os
import time
import requests

try:
    from google import genai
except ImportError:
    genai = None

from cost_calculator import calculate_cost


class LLMProvider:
    def generate(self, prompt):
        raise NotImplementedError


class GeminiProvider(LLMProvider):
    def __init__(self, api_key, model="gemini-2.5-flash"):
        if genai is None:
            raise RuntimeError("Install google-genai to use Gemini.")
        self.client = genai.Client(api_key=api_key)
        self.model = model

    def generate(self, prompt):
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )
        usage = getattr(response, "usage_metadata", None)
        return {
            "response": response.text or "",
            "input_tokens": getattr(usage, "prompt_token_count", 0) or 0,
            "output_tokens": getattr(usage, "candidates_token_count", 0) or 0,
        }


class OllamaProvider(LLMProvider):
    def __init__(self, model="llama3.2", url="http://localhost:11434/api/generate"):
        self.model = model
        self.url = url

    def generate(self, prompt):
        response = requests.post(
            self.url,
            json={"model": self.model, "prompt": prompt, "stream": False},
            timeout=180,
        )
        response.raise_for_status()
        data = response.json()
        return {
            "response": data.get("response", ""),
            "input_tokens": data.get("prompt_eval_count", 0),
            "output_tokens": data.get("eval_count", 0),
        }


class LLMClient:
    def __init__(self, provider, logger=None):
        self.provider = provider
        self.logger = logger

    def generate(self, prompt):
        max_attempts = 3
        start_time = time.perf_counter()
        last_error = None

        for attempt in range(1, max_attempts + 1):
            try:
                result = self.provider.generate(prompt)
                latency = round((time.perf_counter() - start_time) * 1000, 2)
                input_tokens = result.get("input_tokens", 0)
                output_tokens = result.get("output_tokens", 0)
                model = self.provider.model
                provider_name = type(self.provider).__name__
                cost = calculate_cost(
                    provider_name, model, input_tokens, output_tokens
                )

                log_data = {
                    "provider": provider_name,
                    "model": model,
                    "prompt": prompt,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": input_tokens + output_tokens,
                    "latency_ms": latency,
                    "cost": cost,
                    "attempts": attempt,
                    "status": "success",
                    "error": None,
                }
                self._safe_log(log_data)
                return result["response"]

            except Exception as error:
                last_error = error
                retryable = isinstance(
                    error,
                    (requests.exceptions.Timeout, requests.exceptions.ConnectionError),
                )
                if isinstance(error, requests.exceptions.HTTPError):
                    status = error.response.status_code if error.response is not None else None
                    retryable = status == 429 or (status is not None and status >= 500)

                if not retryable or attempt == max_attempts:
                    break

                wait_time = 2 ** (attempt - 1)
                print(f"Attempt {attempt} failed. Retrying in {wait_time}s...")
                time.sleep(wait_time)

        latency = round((time.perf_counter() - start_time) * 1000, 2)
        failed_log = {
            "provider": type(self.provider).__name__,
            "model": getattr(self.provider, "model", "unknown"),
            "prompt": prompt,
            "latency_ms": latency,
            "attempts": attempt,
            "status": "failed",
            "error": str(last_error),
        }
        self._safe_log(failed_log)
        raise last_error

    def _safe_log(self, log_data):
        if self.logger is None:
            return
        try:
            self.logger.log_call(log_data)
        except Exception as log_error:
            # Logging failure should not cause a successful LLM request to be repeated.
            print("MongoDB logging error:", log_error)
