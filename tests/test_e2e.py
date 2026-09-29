import os
import requests
import time
import json
import psycopg2
import psycopg2.extras

# Configurações
WEBHOOK_URL = "http://localhost:3000/webhook"
WEBHOOK_SECRET = "0C841B614950-4305-8F71-2069AB030159" # Pega do .env
DB_HOST = "localhost"
DB_PORT = 5433 # A porta exposta no docker-compose
DB_NAME = "luminus"
DB_USER = "luminus_user"
DB_PASSWORD = os.getenv("LUMINUS_DB_PASSWORD", "")

# --- Teste de Integração End-to-End ---

def test_e2e_flow():
    print("\n--- Iniciando teste de fluxo E2E ---")
    user_id = f"test_user_e2e_{int(time.time())}"
    sender_name = "Silvano"
    
    # Simula uma mensagem simples para o nó GEMINI (padrão)
    test_message_gemini = {
        "data": {
            "key": {"remoteJid": f"{user_id}@s.whatsapp.net", "fromMe": False, "id": "E2E_MSG_1"},
            "message": {"conversation": "Oi LUMINUS, como está o tempo hoje?"},
            "pushName": sender_name
        }
    }
    
    # Simula uma mensagem para forçar o contexto SAC
    test_message_sac = {
        "data": {
            "key": {"remoteJid": f"{user_id}@s.whatsapp.net", "fromMe": False, "id": "E2E_MSG_2"},
            "message": {"conversation": "/sac Olá, preciso rastrear meu pedido"},
            "pushName": sender_name
        }
    }

    # Simula uma mensagem para forçar o contexto SECRETARIA
    test_message_secretary = {
        "data": {
            "key": {"remoteJid": f"{user_id}@s.whatsapp.net", "fromMe": False, "id": "E2E_MSG_3"},
            "message": {"conversation": "/secretary Pode verificar minha agenda para amanhã?"},
            "pushName": sender_name
        }
    }
    
    # Simula uma mensagem para forçar o nó MOBILE
    test_message_mobile = {
        "data": {
            "key": {"remoteJid": f"{user_id}@s.whatsapp.net", "fromMe": False, "id": "E2E_MSG_4"},
            "message": {"conversation": "/mobile Teste de nó mobile"},
            "pushName": sender_name
        }
    }

    messages_to_test = [
        (test_message_gemini,    "general",   "Oi LUMINUS, como está o tempo hoje?"),
        (test_message_sac,       "sac",        "/sac Olá, preciso rastrear meu pedido"),
        (test_message_secretary, "secretary",  "/secretary Pode verificar minha agenda para amanhã?"),
        (test_message_mobile,    "mobile",     "/mobile Teste de nó mobile")
    ]

    headers = {"Authorization": f"Bearer {WEBHOOK_SECRET}", "Content-Type": "application/json"}

    for i, (message, expected_node, original_text) in enumerate(messages_to_test):
        print(f"\n--- Testando Mensagem {i+1}: '{original_text}' ---")
        
        # 1. Enviar para o Webhook
        try:
            response = requests.post(WEBHOOK_URL, json=message, headers=headers, timeout=10)
            assert response.status_code == 200, f"Webhook falhou com status {response.status_code}: {response.text}"
            response_json = response.json()
            assert response_json.get("status") == "queued", f"Webhook não retornou status 'queued': {response_json}"
            print("Webhook respondeu com sucesso (mensagem enfileirada).")
        except requests.exceptions.RequestException as e:
            print(f"Erro ao conectar ao webhook: {e}")
            return False
        
        # 2. Aguarda processamento, maior que o cooldown de 10s do router
        print("Aguardando 12 segundos para o worker processar...")
        time.sleep(12)

        # 3. Verificar o banco de dados
        try:
            conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            full_user_id = f"{user_id}@s.whatsapp.net"
            # Verificar se a mensagem do usuário foi salva
            cur.execute("SELECT m.content, c.context_type FROM messages m JOIN conversations c ON m.conversation_id = c.id WHERE m.role = 'user' AND m.content ILIKE %s AND c.user_id = %s ORDER BY m.created_at DESC LIMIT 1", ('%' + original_text.split(' ')[-1] + '%', full_user_id))
            user_message_record = cur.fetchone()
            
            assert user_message_record, "Mensagem do usuário não encontrada no banco de dados."
            print(f"Mensagem do usuário encontrada no DB: '{user_message_record['content'][:50]}...' coberto com contexto: {user_message_record['context_type']}")
            
            # Verificar o contexto do usuário
            assert user_message_record['context_type'] == expected_node, \
                f"Contexto incorreto no DB. Esperado: '{expected_node}', Encontrado: '{user_message_record['context_type']}'"
            
            # Verificar se a resposta do assistente foi salva (a resposta real pode variar)
            cur.execute("SELECT m.content FROM messages m JOIN conversations c ON m.conversation_id = c.id WHERE m.role = 'assistant' AND c.user_id = %s ORDER BY m.created_at DESC LIMIT 1", (full_user_id,))
            assistant_message_record = cur.fetchone()
            assert assistant_message_record, "Resposta do assistente não encontrada no banco de dados."
            print(f"Resposta do assistente encontrada no DB: '{assistant_message_record['content'][:50]}...' (Verificação parcial)")

            conn.close()
            
        except psycopg2.Error as e:
            print(f"Erro ao conectar ou consultar o banco de dados: {e}")
            return False
        
    print(f"--- Teste {i+1} passou com sucesso ---")
    
    # Pequena pausa entre testes para não sobrecarregar tudo
    time.sleep(1)

    return True

if __name__ == "__main__":
    print("Iniciando execução dos testes...")
    all_passed = True
    if not test_e2e_flow():
        all_passed = False

    if all_passed:
        print("\n--- TODOS OS TESTES E2E PASSARAM COM SUCESSO! ---")
    else:
        print("\n--- FALHA EM UM OU MAIS TESTES E2E! ---")
