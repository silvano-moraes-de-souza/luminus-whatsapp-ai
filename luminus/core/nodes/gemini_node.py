# ================================================================
# LUMINUS - ASSISTENTE PESSOAL PERSONALIZADO
# ARQUIVO: gemini_node.py
# DESCRIÇÃO: Nó de processamento via Google Gemini API
# AUTOR: SILVANO MORAES DE SOUZA
# VERSÃO: 1.0.4
# ================================================================

import os
import logging
from luminus.core.nodes.base_node import BaseNode
from luminus.core.models import MessageTask
from luminus.core.persona import get_persona
from luminus.core.contacts import is_contact_allowed

GEMINI_MODELS = [
    'gemini-2.5-flash-native-audio-preview',
    'gemini-2.5-flash-preview',
    'gemini-2.5-flash',
    'gemini-2.0-flash',
    'gemini-2.0-flash-001',
    'gemini-2.0-flash-lite-001',
    'gemini-2.0-flash-lite',
    'gemini-flash-latest',
    'gemini-flash-lite-latest',
    'gemini-pro-latest',
    'gemini-2.5-flash-lite',
    'gemma-3-27b-it',
    'gemma-3-12b-it',
    'gemma-3-4b-it',
    'gemma-3-1b-it',
    'gemma-4-31b-it',
]

class GeminiNode(BaseNode):
    def __init__(self) -> None:
        api_key = os.getenv("GEMINI_API_KEY_PRIMARY")
        self.last_model: str | None = None
        if api_key:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
    
    @property
    def name(self) -> str:
        return "IA_GEMINI_POOL"

    def execute(self, task: MessageTask) -> str:
        owner = os.getenv("OWNER_NUMBER", "")
        is_silvano = bool(owner) and owner in task.user_id
        
        if not is_contact_allowed(task.user_id, task.sender_name):
            return "[SILENT_IGNORE]"
        
        api_keys = [
            os.getenv("GEMINI_API_KEY_PRIMARY"),
            os.getenv("GEMINI_API_KEY_FALLBACK")
        ]
        api_keys = [key for key in api_keys if key and not key.startswith("INSIRA_")]
        
        if not api_keys:
            raise Exception("Nenhuma GEMINI_API_KEY configurada no .env")
        
        history = []
        for msg in task.history:
            role = "user" if msg["role"] == "user" else "model"
            history.append({"role": role, "parts": [{"text": msg["content"]}]})
        
        history.append({"role": "user", "parts": [{"text": task.text}]})
        
        system_msg = get_persona(is_silvano, task.sender_name)
        
        import google.generativeai as genai
        
        for api_key in api_keys[:3]:
            try:
                genai.configure(api_key=api_key)
                
                for model_name in GEMINI_MODELS[:5]:
                    try:
                        logging.info(f"[{self.name}] Tentando modelo: {model_name}")
                        model = genai.GenerativeModel(model_name)
                        
                        history_msg = [{"role": "user", "parts": [{"text": system_msg}]}] + history
                        
                        response = model.generate_content(
                            history_msg,
                            generation_config={
                                "temperature": 0.7,
                                "top_p": 0.95,
                                "max_output_tokens": 2048,
                            }
                        )
                        
                        text_out = response.text.strip() if response.text else "OK"
                        
                        if "[SILENT_IGNORE]" in text_out:
                            return "[SILENT_IGNORE]"
                        
                        self.last_model = model_name
                        logging.info(f"[{self.name}] SUCESSO com {model_name}")
                        return text_out
                        
                    except Exception as e:
                        erro = str(e)[:100]
                        if "API key not valid" in erro or "Permission denied" in erro or "403" in erro or "400" in erro:
                            logging.warning(f"[{self.name}] ERRO de API key: {erro}")
                            break
                        else:
                            logging.warning(f"[{self.name}] ERRO em {model_name}: {erro}")
                            continue
            except Exception as e:
                logging.warning(f"[{self.name}] ERRO ao configurar chave: {str(e)[:100]}")
                continue
        
        raise Exception("Todas as chaves API e modelos falharam.")