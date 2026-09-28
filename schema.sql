-- Schema do Banco de Dados LUMINUS
-- Estrutura para suportar o histórico de mensagens e estado do SAC/Secretaria

CREATE TABLE IF NOT EXISTS conversations (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) UNIQUE NOT NULL,
    sender_name VARCHAR(255),
    last_interaction TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    context_type VARCHAR(50) DEFAULT 'general' -- 'secretary' ou 'sac'
);

CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id),
    role VARCHAR(50), -- 'user' ou 'assistant'
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS state (
    conversation_id INTEGER REFERENCES conversations(id) UNIQUE,
    current_intent VARCHAR(100),
    metadata JSONB -- Para armazenar dados extras (rastreio, dados de venda)
);
