-- Script de inicialização do PostgreSQL
-- Executado automaticamente quando o container é criado pela primeira vez

-- Configurar timezone
SET timezone = 'America/Sao_Paulo';

-- Criar extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Configurações de performance
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
ALTER SYSTEM SET track_activity_query_size = 2048;
ALTER SYSTEM SET pg_stat_statements.track = 'all';

-- Log de inicialização
DO $$
BEGIN
    RAISE NOTICE '🚀 PostgreSQL inicializado para Sistema NFE';
    RAISE NOTICE '📊 Banco: nfedb';
    RAISE NOTICE '👤 Usuário: nfeuser';
    RAISE NOTICE '🔧 Timezone: America/Sao_Paulo';
END $$;
