import os
import openai
import requests
import datetime

class LLMClient:
    def __init__(self, backend=None, openai_api_key=None, lmstudio_url=None):
        self.backend = backend or os.environ.get('LLM_BACKEND', 'openai')
        self.openai_api_key = openai_api_key or os.environ.get('OPENAI_API_KEY')
        self.lmstudio_url = lmstudio_url or os.environ.get('LMSTUDIO_URL', 'http://192.168.86.101:1234/v1/chat/completions')
        if self.backend == 'openai':
            openai.api_key = self.openai_api_key

    def generate_resume(self, prompt, model='gpt-4o', max_tokens=1800, temperature=0.7):
        if self.backend == 'openai':
            return self._openai_chat(prompt, model, max_tokens, temperature)
        elif self.backend == 'lmstudio':
            return self._lmstudio_chat(prompt, model, max_tokens, temperature)
        else:
            raise ValueError(f"Unknown LLM backend: {self.backend}")

    def generate_cover_letter(self, prompt, model='gpt-4o', max_tokens=1200, temperature=0.7):
        if self.backend == 'openai':
            return self._openai_chat(prompt, model, max_tokens, temperature)
        elif self.backend == 'lmstudio':
            return self._lmstudio_chat(prompt, model, max_tokens, temperature)
        else:
            raise ValueError(f"Unknown LLM backend: {self.backend}")

    def _openai_chat(self, prompt, model, max_tokens, temperature):
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert career advisor."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].message.content.strip()

    def _lmstudio_chat(self, prompt, model, max_tokens, temperature):
        # LMStudio REST API (non-OpenAI compatible)
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are an expert career advisor."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        resp = requests.post(self.lmstudio_url, json=payload, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()
