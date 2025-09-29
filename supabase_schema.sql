-- =====================================================
-- SCHEMA COMPLETO PARA SUPABASE - SISTEMA NFE
-- =====================================================

-- 1. CRIAR ENUMS
-- =====================================================

-- Enum para roles de usuário
CREATE TYPE userrole AS ENUM ('admin', 'editor', 'viewer');

-- Enum para ações de auditoria
CREATE TYPE auditaction AS ENUM ('create', 'update', 'delete');

-- Enum para origem de preços
CREATE TYPE origempreco AS ENUM ('manual', 'nota_xml', 'nota_pdf', 'api');

-- Enum para status de notas
CREATE TYPE statusnota AS ENUM ('rascunho', 'processando', 'processada', 'falha');

-- 2. TABELA DE USUÁRIOS
-- =====================================================
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    password_hash VARCHAR NOT NULL,
    role userrole NOT NULL DEFAULT 'viewer',
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Índices para users
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_id ON users(id);

-- 3. TABELA DE UNIDADES DE MEDIDA
-- =====================================================
CREATE TABLE unidades (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(10) UNIQUE NOT NULL,
    descricao VARCHAR NOT NULL,
    fator_para_menor NUMERIC(10, 4),
    menor_unidade_codigo VARCHAR(10) REFERENCES unidades(codigo),
    is_base BOOLEAN NOT NULL DEFAULT false
);

-- Índices para unidades
CREATE INDEX idx_unidades_codigo ON unidades(codigo);
CREATE INDEX idx_unidades_id ON unidades(id);

-- 4. TABELA DE FORNECEDORES
-- =====================================================
CREATE TABLE fornecedores (
    id SERIAL PRIMARY KEY,
    cnpj VARCHAR(18) UNIQUE NOT NULL,
    nome VARCHAR NOT NULL,
    endereco VARCHAR,
    ativo BOOLEAN NOT NULL DEFAULT true,
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    atualizado_em TIMESTAMP WITH TIME ZONE
);

-- Índices para fornecedores
CREATE INDEX idx_fornecedores_cnpj ON fornecedores(cnpj);
CREATE INDEX idx_fornecedores_id ON fornecedores(id);

-- 5. TABELA DE MATÉRIAS-PRIMAS
-- =====================================================
CREATE TABLE materias_primas (
    id SERIAL PRIMARY KEY,
    nome VARCHAR UNIQUE NOT NULL,
    unidade_codigo VARCHAR(10) NOT NULL REFERENCES unidades(codigo),
    menor_unidade_codigo VARCHAR(10) REFERENCES unidades(codigo),
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Índices para materias_primas
CREATE INDEX idx_materias_primas_nome ON materias_primas(nome);
CREATE INDEX idx_materias_primas_id ON materias_primas(id);

-- 6. TABELA DE NOTAS FISCAIS
-- =====================================================
CREATE TABLE notas (
    id SERIAL PRIMARY KEY,
    numero VARCHAR(50) NOT NULL,
    serie VARCHAR,
    chave_acesso VARCHAR(44) UNIQUE,
    fornecedor_id INTEGER REFERENCES fornecedores(id),
    emissao_date DATE NOT NULL,
    valor_total FLOAT NOT NULL,
    arquivo_xml_path VARCHAR,
    arquivo_pdf_path VARCHAR,
    file_hash VARCHAR(32) UNIQUE,
    status statusnota NOT NULL DEFAULT 'rascunho',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT true
);

-- Índices para notas
CREATE INDEX idx_notas_id ON notas(id);
CREATE INDEX idx_notas_chave_acesso ON notas(chave_acesso);
CREATE INDEX idx_notas_fornecedor_id ON notas(fornecedor_id);
CREATE INDEX idx_notas_file_hash ON notas(file_hash);

-- 7. TABELA DE ITENS DAS NOTAS FISCAIS
-- =====================================================
CREATE TABLE nota_itens (
    id SERIAL PRIMARY KEY,
    nota_id INTEGER NOT NULL REFERENCES notas(id) ON DELETE CASCADE,
    materia_prima_id INTEGER REFERENCES materias_primas(id),
    nome_no_documento VARCHAR NOT NULL,
    unidade_codigo VARCHAR(10) NOT NULL REFERENCES unidades(codigo),
    quantidade FLOAT NOT NULL,
    valor_unitario FLOAT NOT NULL,
    valor_total FLOAT NOT NULL
);

-- Índices para nota_itens
CREATE INDEX idx_nota_itens_id ON nota_itens(id);
CREATE INDEX idx_nota_itens_nota_id ON nota_itens(nota_id);
CREATE INDEX idx_nota_itens_materia_prima_id ON nota_itens(materia_prima_id);

-- 8. TABELA DE PREÇOS DE MATÉRIAS-PRIMAS
-- =====================================================
CREATE TABLE materia_prima_precos (
    id SERIAL PRIMARY KEY,
    materia_prima_id INTEGER NOT NULL REFERENCES materias_primas(id),
    valor_unitario NUMERIC(14, 4) NOT NULL,
    moeda VARCHAR(3) NOT NULL DEFAULT 'BRL',
    vigente_desde TIMESTAMP WITH TIME ZONE NOT NULL,
    vigente_ate TIMESTAMP WITH TIME ZONE,
    fornecedor_id INTEGER REFERENCES fornecedores(id),
    nota_id INTEGER REFERENCES notas(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para materia_prima_precos
CREATE INDEX idx_materia_prima_precos_id ON materia_prima_precos(id);
CREATE INDEX idx_materia_prima_precos_materia_prima_id ON materia_prima_precos(materia_prima_id);
CREATE INDEX idx_materia_prima_precos_vigente_desde ON materia_prima_precos(vigente_desde);

-- 9. TABELA DE PRODUTOS FINAIS
-- =====================================================
CREATE TABLE produtos (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR UNIQUE NOT NULL,
    nome VARCHAR NOT NULL,
    descricao VARCHAR,
    categoria VARCHAR,
    unidade_medida VARCHAR,
    preco_custo FLOAT,
    preco_venda FLOAT,
    estoque_minimo FLOAT,
    estoque_atual FLOAT,
    fornecedor_id INTEGER REFERENCES fornecedores(id),
    ativo BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Índices para produtos
CREATE INDEX idx_produtos_codigo ON produtos(codigo);
CREATE INDEX idx_produtos_id ON produtos(id);

-- 10. TABELA DE COMPONENTES DOS PRODUTOS
-- =====================================================
CREATE TABLE produto_componentes (
    id SERIAL PRIMARY KEY,
    produto_id INTEGER NOT NULL REFERENCES produtos(id) ON DELETE CASCADE,
    materia_prima_id INTEGER NOT NULL REFERENCES materias_primas(id),
    quantidade FLOAT NOT NULL,
    unidade_codigo VARCHAR(10) NOT NULL REFERENCES unidades(codigo)
);

-- Índices para produto_componentes
CREATE INDEX idx_produto_componentes_id ON produto_componentes(id);
CREATE INDEX idx_produto_componentes_produto_id ON produto_componentes(produto_id);
CREATE INDEX idx_produto_componentes_materia_prima_id ON produto_componentes(materia_prima_id);

-- 11. TABELA DE PREÇOS DOS PRODUTOS
-- =====================================================
CREATE TABLE produto_precos (
    id SERIAL PRIMARY KEY,
    produto_id INTEGER NOT NULL REFERENCES produtos(id),
    custo_total FLOAT NOT NULL,
    vigente_desde TIMESTAMP WITH TIME ZONE NOT NULL,
    vigente_ate TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para produto_precos
CREATE INDEX idx_produto_precos_id ON produto_precos(id);
CREATE INDEX idx_produto_precos_produto_id ON produto_precos(produto_id);
CREATE INDEX idx_produto_precos_vigente_desde ON produto_precos(vigente_desde);

-- 12. TABELA DE LOGS DE AUDITORIA
-- =====================================================
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    entity VARCHAR NOT NULL,
    entity_id INTEGER NOT NULL,
    action auditaction NOT NULL,
    changes JSONB,
    ip_address VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para audit_logs
CREATE INDEX idx_audit_logs_id ON audit_logs(id);
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_entity ON audit_logs(entity);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);

-- 13. DADOS INICIAIS - UNIDADES DE MEDIDA
-- =====================================================
INSERT INTO unidades (codigo, descricao, fator_para_menor, is_base) VALUES
('UN', 'Unidade', 1.0, true),
('KG', 'Quilograma', 1000.0, true),
('G', 'Grama', 1.0, false),
('L', 'Litro', 1000.0, true),
('ML', 'Mililitro', 1.0, false),
('M', 'Metro', 100.0, true),
('CM', 'Centímetro', 1.0, false),
('M2', 'Metro Quadrado', 10000.0, true),
('CM2', 'Centímetro Quadrado', 1.0, false),
('CX', 'Caixa', 1.0, true),
('PC', 'Peça', 1.0, true),
('ROL', 'Rolo', 1.0, true),
('BOB', 'Bobina', 1.0, true);

-- Atualizar referências de menor unidade
UPDATE unidades SET menor_unidade_codigo = 'G' WHERE codigo = 'KG';
UPDATE unidades SET menor_unidade_codigo = 'ML' WHERE codigo = 'L';
UPDATE unidades SET menor_unidade_codigo = 'CM' WHERE codigo = 'M';
UPDATE unidades SET menor_unidade_codigo = 'CM2' WHERE codigo = 'M2';

-- 14. FORNECEDOR PADRÃO
-- =====================================================
INSERT INTO fornecedores (cnpj, nome, endereco, ativo) VALUES
('00000000000000', 'Fornecedor Padrão', 'Endereço não disponível', true);

-- 15. USUÁRIO ADMIN PADRÃO (senha: admin123)
-- =====================================================
INSERT INTO users (name, email, password_hash, role, is_active) VALUES
('Administrador', 'admin@sistema.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J5K5K5K5K', 'admin', true);

-- 16. COMENTÁRIOS DAS TABELAS
-- =====================================================
COMMENT ON TABLE users IS 'Usuários do sistema com diferentes níveis de acesso';
COMMENT ON TABLE unidades IS 'Unidades de medida utilizadas no sistema';
COMMENT ON TABLE fornecedores IS 'Fornecedores de matérias-primas e produtos';
COMMENT ON TABLE materias_primas IS 'Matérias-primas utilizadas na produção';
COMMENT ON TABLE notas IS 'Notas fiscais importadas e processadas';
COMMENT ON TABLE nota_itens IS 'Itens individuais das notas fiscais';
COMMENT ON TABLE materia_prima_precos IS 'Histórico de preços das matérias-primas';
COMMENT ON TABLE produtos IS 'Produtos finais fabricados';
COMMENT ON TABLE produto_componentes IS 'Composição dos produtos (matérias-primas + quantidades)';
COMMENT ON TABLE produto_precos IS 'Histórico de custos dos produtos finais';
COMMENT ON TABLE audit_logs IS 'Log de auditoria de todas as operações do sistema';

-- =====================================================
-- FIM DO SCHEMA
-- =====================================================



