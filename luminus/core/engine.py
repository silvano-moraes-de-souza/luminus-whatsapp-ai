# ================================================================
# LUMINUS - ASSISTENTE PESSOAL PERSONALIZADO
# ARQUIVO: engine.py
# DESCRIÇÃO: Motor de IA com pool de modelos para fallback automático
# AUTOR: SILVANO MORAES DE SOUZA
# VERSÃO: 1.0.2
# ================================================================

import os
import requests
import logging

class AIEngine:
    def __init__(self) -> None:
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            logging.error("[AI ENGINE] OPENROUTER_API_KEY não encontrada no .env!")
            
        self.base_url = "https://openrouter.ai/api/v1"
        
        self.models_pool = [
            "google/gemma-3-27b-it:free",
            "meta-llama/llama-3.3-70b-instruct:free",
            "deepseek/deepseek-r1:free",
            "qwen/qwen3-coder:free",
        ]

    def get_response(self, prompt: str, history: list[dict] | None = None) -> str:
        if not self.api_key:
            return "Erro: API Key não configurada."

        if history is None:
            history = []

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://luminus.app",
            "X-Title": "Luminus Assistente",
        }

        system_prompt = {
            "role": "system",
            "content": (
                "Você é o Luminus, assistente pessoal de Silvano Moraes de Souza. "
                "Responda de forma direta, técnica e sem rodeios."
            )
        }

        messages = [system_prompt]
        for msg in history:
            messages.append({
                "role": "user" if msg["role"] == "user" else "assistant",
                "content": msg["content"]
            })
        messages.append({"role": "user", "content": prompt})

        models_tried = 0
        max_models = 3
        
        for model in self.models_pool:
            if models_tried >= max_models:
                break
            models_tried += 1
            
            try:
                logging.info(f"[AI ENGINE] Tentando modelo: {model}")
                
                payload = {
                    "model": model,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 1000
                }

                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "choices" in data and len(data["choices"]) > 0:
                        res_content = data["choices"][0]["message"]["content"]
                        logging.info(f"[AI ENGINE] Sucesso com {model}!")
                        return res_content
                    else:
                        logging.warning(f"[AI ENGINE] Resposta vazia de {model}.")
                        continue
                
                elif response.status_code == 429:
                    logging.warning(f"[AI ENGINE] Rate Limit (429) no {model}.")
                    continue
                elif response.status_code == 404:
                    logging.error(f"[AI ENGINE] Modelo {model} não existe (404).")
                    continue
                else:
                    logging.error(f"[AI ENGINE] Falha no {model} Status:{response.status_code}")
                    continue 

            except Exception as e:
                logging.error(f"[AI ENGINE] Exceção no {model}: {str(e)}")
                continue 

        return "Desculpe Silvano, os serviços de IA estão indisponíveis no momento."