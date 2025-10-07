"""Fix tables

Revision ID: 0003
Revises: 0002
Create Date: 2025-10-07 20:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0003'
down_revision = '0002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Renomear tabela fornecedores para fornecedor
    op.execute("ALTER TABLE IF EXISTS fornecedores RENAME TO fornecedor")
    op.execute("ALTER INDEX IF EXISTS ix_fornecedores_id RENAME TO ix_fornecedor_id")
    op.execute("ALTER INDEX IF EXISTS ix_fornecedores_cnpj RENAME TO ix_fornecedor_cnpj")
    op.execute("ALTER SEQUENCE IF EXISTS fornecedores_id_seq RENAME TO fornecedor_id_seq")
    
    # Renomear a coluna id para id_fornecedor
    op.execute("ALTER TABLE IF EXISTS fornecedor RENAME COLUMN id TO id_fornecedor")
    
    # Renomear is_active para ativo
    op.execute("ALTER TABLE IF EXISTS fornecedor RENAME COLUMN is_active TO ativo")
    
    # 2. Adicionar colunas faltando em notas
    op.execute("ALTER TABLE IF EXISTS notas ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true NOT NULL")
    op.execute("ALTER TABLE IF EXISTS notas ADD COLUMN IF NOT EXISTS is_pinned BOOLEAN DEFAULT false NOT NULL")
    
    # Alterar tipo da coluna numero para VARCHAR
    op.execute("ALTER TABLE IF EXISTS notas ALTER COLUMN numero TYPE VARCHAR(50)")
    
    # 3. Corrigir tabela unidades - adicionar menor_unidade_id
    op.execute("""
        ALTER TABLE IF EXISTS unidades 
        ADD COLUMN IF NOT EXISTS menor_unidade_id INTEGER
    """)
    
    # Criar FK para menor_unidade_id
    op.execute("""
        DO $$
        BEGIN
            ALTER TABLE unidades 
            ADD CONSTRAINT fk_unidades_menor_unidade_id 
            FOREIGN KEY (menor_unidade_id) 
            REFERENCES unidades(id);
        EXCEPTION
            WHEN duplicate_object THEN
                NULL;
        END $$;
    """)
    
    # 4. Criar tabela produtos_finais
    op.execute("""
        CREATE TABLE IF NOT EXISTS produtos_finais (
            id SERIAL PRIMARY KEY,
            nome VARCHAR NOT NULL,
            descricao VARCHAR,
            id_unico VARCHAR,
            componentes JSONB,
            ativo BOOLEAN DEFAULT true NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE
        )
    """)
    
    op.execute("CREATE INDEX IF NOT EXISTS ix_produtos_finais_id ON produtos_finais(id)")
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS ix_produtos_finais_nome ON produtos_finais(nome)")


def downgrade() -> None:
    # Reverter mudanças
    op.drop_table('produtos_finais')
    op.execute("ALTER TABLE IF EXISTS unidades DROP COLUMN IF EXISTS menor_unidade_id")
    op.execute("ALTER TABLE IF EXISTS notas DROP COLUMN IF EXISTS is_active")
    op.execute("ALTER TABLE IF EXISTS notas DROP COLUMN IF EXISTS is_pinned")
    op.execute("ALTER TABLE IF EXISTS notas ALTER COLUMN numero TYPE INTEGER USING numero::integer")
    op.execute("ALTER TABLE IF EXISTS fornecedor RENAME COLUMN ativo TO is_active")
    op.execute("ALTER TABLE IF EXISTS fornecedor RENAME COLUMN id_fornecedor TO id")
    op.execute("ALTER TABLE IF EXISTS fornecedor RENAME TO fornecedores")
    op.execute("ALTER INDEX IF EXISTS ix_fornecedor_id RENAME TO ix_fornecedores_id")
    op.execute("ALTER INDEX IF EXISTS ix_fornecedor_cnpj RENAME TO ix_fornecedores_cnpj")

