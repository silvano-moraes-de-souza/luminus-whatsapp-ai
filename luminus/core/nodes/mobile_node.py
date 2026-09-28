# ================================================================
# LUMINUS - ASSISTENTE PESSOAL PERSONALIZADO
# ARQUIVO: mobile_node.py
# DESCRIÇÃO: Nó de processamento via modelo local (LM Studio)
# AUTOR: SILVANO MORAES DE SOUZA
# VERSÃO: 1.0.2
# ================================================================

import requests
import os
import logging
from luminus.core.nodes.base_node import BaseNode
from luminus.core.models import MessageTask

class MobileNode(BaseNode):
    @property
    def name(self) -> str:
        return "IA_MOBILE_EDGE"

    def execute(self, task: MessageTask) -> str:
        url = os.getenv("MOBILE_API_URL", "http://localhost:1234/v1/chat/completions")
        
        headers = {"Content-Type": "application/json"}
        
        messages = [{"role": "system", "content": "Você é o Luminus no dispositivo local."}]
        for msg in task.history:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": task.text})

        payload = {
            "model": "local-model",
            "messages": messages,
            "temperature": 0.7
        }

        try:
            logging.info(f"[{self.name}] Chamando LM Studio em {url}")
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"]
            else:
                raise Exception(f"Erro HTTP {response.status_code}")
                
        except Exception as e:
            logging.error(f"[{self.name}] Falha de conexão: {e}")
            raise e