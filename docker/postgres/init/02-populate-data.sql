-- Script para popular dados iniciais no PostgreSQL
-- Executado automaticamente após a criação do banco

-- Configurar timezone
SET timezone = 'America/Sao_Paulo';

-- Log de inicialização
DO $$
BEGIN
    RAISE NOTICE '🌱 Iniciando população de dados do Sistema NFE...';
END $$;

-- Aguardar um pouco para garantir que as extensões estejam carregadas
SELECT pg_sleep(2);

-- Log de conclusão
DO $$
BEGIN
    RAISE NOTICE '✅ Script de inicialização do PostgreSQL concluído!';
    RAISE NOTICE '📊 Banco nfedb pronto para receber dados via Alembic e Seeds';
END $$;
