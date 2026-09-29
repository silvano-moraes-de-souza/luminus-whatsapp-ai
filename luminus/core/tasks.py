import os
from celery import Celery
from luminus.core.router import MessageRouter
from luminus.core.db_manager import DatabaseManager
from luminus.core.integrations.google_adapter import GoogleAdapter
import requests
import logging

# Configuração do Celery: lê do env para suportar Docker e execução local
_REDIS_URL = os.getenv('REDIS_URL', 'redis://luminus_redis:6379/0')
celery_app = Celery(
    'luminus',
    broker=_REDIS_URL,
    backend=_REDIS_URL
)

# Inicializa dependências globais (fora do escopo da task para evitar recriação)
router = MessageRouter()
db_manager = DatabaseManager()
google_adapter = GoogleAdapter() # Mocked for now

EVO_API_URL = os.getenv("EVOLUTION_API_URL")
EVO_API_KEY = os.getenv("EVOLUTION_API_KEY")
INSTANCE_NAME = os.getenv("INSTANCE_NAME")

@celery_app.task(name='tasks.process_whatsapp_message', bind=True, max_retries=3)
def process_whatsapp_message(self, sender, message_text, push_name, is_audio):
    try:
        logging.info(f"[TASK] Processando mensagem de {sender}")
        
        # Determina o contexto e busca histórico (agora do DB)
        context_type = db_manager.get_conversation_context(sender)
        # O router internamente usa o db_manager para obter o histórico

        # Chama o router para processar a lógica
        response_text = router.process_message(
            sender,
            message_text,
            sender_name=push_name,
            is_audio=is_audio
        )

        # Salva a resposta do assistente no banco
        # O router já adiciona a mensagem do usuário antes de processar
        # A resposta do assistente também precisa ser salva
        db_manager.add_message(sender, push_name, "assistant", response_text)

        if response_text and "[SILENT_IGNORE]" not in response_text:
            send_whatsapp_message(sender, response_text)
            
        return {"status": "success", "recipient": sender}

    except Exception as e:
        logging.error(f"[TASK] Erro ao processar mensagem para {sender}: {e}")
        # Tenta novamente em caso de falha, com backoff
        raise self.retry(exc=e, countdown=10)


def send_whatsapp_message(number, text):
    url = f"{EVO_API_URL}/message/sendText/{INSTANCE_NAME}"
    headers = {"apikey": EVO_API_KEY, "Content-Type": "application/json"}
    payload = {"number": number, "text": text, "linkPreview": False}

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        if response.status_code in [200, 201]:
            logging.info(f"[TASK] RESPOSTA ENVIADA para {number}")
        else:
            logging.error(f"[TASK] ERRO EVOLUTION API: {response.status_code} - {response.text}")
    except Exception as e:
        logging.error(f"[TASK] ERRO TRANSPORTE: {e}")

