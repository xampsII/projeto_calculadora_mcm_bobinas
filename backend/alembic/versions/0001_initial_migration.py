"""Initial migration

Revision ID: 0001
Revises: 
Create Date: 2025-01-27 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum types (idempotent)
    op.execute("""
    DO $$
    BEGIN
        CREATE TYPE userrole AS ENUM ('admin', 'editor', 'viewer');
    EXCEPTION
        WHEN duplicate_object THEN
            -- tipo já existe; não faz nada
            NULL;
    END $$;
    """)
    
    op.execute("""
    DO $$
    BEGIN
        CREATE TYPE auditaction AS ENUM ('create', 'update', 'delete');
    EXCEPTION
        WHEN duplicate_object THEN
            NULL;
    END $$;
    """)
    
    op.execute("""
    DO $$
    BEGIN
        CREATE TYPE origempreco AS ENUM ('manual', 'nota_xml', 'nota_pdf', 'api');
    EXCEPTION
        WHEN duplicate_object THEN
            NULL;
    END $$;
    """)
    
    op.execute("""
    DO $$
    BEGIN
        CREATE TYPE statusnota AS ENUM ('rascunho', 'processando', 'processada', 'falha');
    EXCEPTION
        WHEN duplicate_object THEN
            NULL;
    END $$;
    """)
    
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('password_hash', sa.String(), nullable=False),
        sa.Column('role', postgresql.ENUM('admin', 'editor', 'viewer', name='userrole', create_type=False), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    
    # Create audit_logs table
    op.create_table('audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('entity', sa.String(), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=False),
        sa.Column('action', postgresql.ENUM('create', 'update', 'delete', name='auditaction', create_type=False), nullable=False),
        sa.Column('changes', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('ip_address', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], )
    )
    op.create_index(op.f('ix_audit_logs_id'), 'audit_logs', ['id'], unique=False)
    
    # Create unidades table
    op.create_table('unidades',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('codigo', sa.String(length=10), nullable=False),
        sa.Column('descricao', sa.String(), nullable=False),
        sa.Column('fator_para_menor', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('menor_unidade_codigo', sa.String(length=10), nullable=True),
        sa.Column('is_base', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_unidades_id'), 'unidades', ['id'], unique=False)
    op.create_index(op.f('ix_unidades_codigo'), 'unidades', ['codigo'], unique=True)
    
    # Create fornecedores table
    op.create_table('fornecedores',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('cnpj', sa.String(length=18), nullable=False),
        sa.Column('nome', sa.String(), nullable=False),
        sa.Column('endereco', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_fornecedores_id'), 'fornecedores', ['id'], unique=False)
    op.create_index(op.f('ix_fornecedores_cnpj'), 'fornecedores', ['cnpj'], unique=True)
    
    # Create materias_primas table
    op.create_table('materias_primas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(), nullable=False),
        sa.Column('unidade_codigo', sa.String(length=10), nullable=False),
        sa.Column('menor_unidade_codigo', sa.String(length=10), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['menor_unidade_codigo'], ['unidades.codigo'], ),
        sa.ForeignKeyConstraint(['unidade_codigo'], ['unidades.codigo'], )
    )
    op.create_index(op.f('ix_materias_primas_id'), 'materias_primas', ['id'], unique=False)
    op.create_index(op.f('ix_materias_primas_nome'), 'materias_primas', ['nome'], unique=True)
    
    # Create notas table
    op.create_table('notas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('numero', sa.Integer(), nullable=False),
        sa.Column('serie', sa.String(length=10), nullable=False),
        sa.Column('chave_acesso', sa.String(length=44), nullable=True),
        sa.Column('fornecedor_id', sa.Integer(), nullable=False),
        sa.Column('emissao_date', sa.Date(), nullable=False),
        sa.Column('valor_total', sa.Numeric(precision=16, scale=4), nullable=False),
        sa.Column('arquivo_xml_path', sa.String(), nullable=True),
        sa.Column('arquivo_pdf_path', sa.String(), nullable=True),
        sa.Column('file_hash', sa.String(length=64), nullable=True),
        sa.Column('status', postgresql.ENUM('rascunho', 'processando', 'processada', 'falha', name='statusnota', create_type=False), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['fornecedor_id'], ['fornecedores.id'], )
    )
    op.create_index(op.f('ix_notas_id'), 'notas', ['id'], unique=False)
    op.create_index(op.f('ix_notas_chave_acesso'), 'notas', ['chave_acesso'], unique=True)
    
    # Create nota_itens table
    op.create_table('nota_itens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nota_id', sa.Integer(), nullable=False),
        sa.Column('materia_prima_id', sa.Integer(), nullable=True),
        sa.Column('nome_no_documento', sa.String(), nullable=False),
        sa.Column('unidade_codigo', sa.String(length=10), nullable=False),
        sa.Column('quantidade', sa.Numeric(precision=18, scale=6), nullable=False),
        sa.Column('valor_unitario', sa.Numeric(precision=14, scale=4), nullable=False),
        sa.Column('valor_total', sa.Numeric(precision=16, scale=4), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['materia_prima_id'], ['materias_primas.id'], ),
        sa.ForeignKeyConstraint(['nota_id'], ['notas.id'], ),
        sa.ForeignKeyConstraint(['unidade_codigo'], ['unidades.codigo'], )
    )
    op.create_index(op.f('ix_nota_itens_id'), 'nota_itens', ['id'], unique=False)
    
    # Create materia_prima_precos table
    op.create_table('materia_prima_precos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('materia_prima_id', sa.Integer(), nullable=False),
        sa.Column('valor_unitario', sa.Numeric(precision=14, scale=4), nullable=False),
        sa.Column('moeda', sa.String(length=3), nullable=False),
        sa.Column('vigente_desde', sa.DateTime(timezone=True), nullable=False),
        sa.Column('vigente_ate', sa.DateTime(timezone=True), nullable=True),
        sa.Column('origem', postgresql.ENUM('manual', 'nota_xml', 'nota_pdf', 'api', name='origempreco', create_type=False), nullable=False),
        sa.Column('fornecedor_id', sa.Integer(), nullable=True),
        sa.Column('nota_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['fornecedor_id'], ['fornecedores.id'], ),
        sa.ForeignKeyConstraint(['materia_prima_id'], ['materias_primas.id'], ),
        sa.ForeignKeyConstraint(['nota_id'], ['notas.id'], )
    )
    op.create_index(op.f('ix_materia_prima_precos_id'), 'materia_prima_precos', ['id'], unique=False)
    
    # Create produtos table
    op.create_table('produtos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_produtos_id'), 'produtos', ['id'], unique=False)
    op.create_index(op.f('ix_produtos_nome'), 'produtos', ['nome'], unique=True)
    
    # Create produto_componentes table
    op.create_table('produto_componentes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('produto_id', sa.Integer(), nullable=False),
        sa.Column('materia_prima_id', sa.Integer(), nullable=False),
        sa.Column('quantidade', sa.Numeric(precision=18, scale=6), nullable=False),
        sa.Column('unidade_codigo', sa.String(length=10), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['materia_prima_id'], ['materias_primas.id'], ),
        sa.ForeignKeyConstraint(['produto_id'], ['produtos.id'], ),
        sa.ForeignKeyConstraint(['unidade_codigo'], ['unidades.codigo'], )
    )
    op.create_index(op.f('ix_produto_componentes_id'), 'produto_componentes', ['id'], unique=False)
    
    # Create produto_precos table
    op.create_table('produto_precos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('produto_id', sa.Integer(), nullable=False),
        sa.Column('custo_total', sa.Numeric(precision=16, scale=4), nullable=False),
        sa.Column('vigente_desde', sa.DateTime(timezone=True), nullable=False),
        sa.Column('vigente_ate', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['produto_id'], ['produtos.id'], )
    )
    op.create_index(op.f('ix_produto_precos_id'), 'produto_precos', ['id'], unique=False)
    
    # Add foreign key constraints for unidades self-reference
    op.create_foreign_key(None, 'unidades', 'unidades', ['menor_unidade_codigo'], ['codigo'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('produto_precos')
    op.drop_table('produto_componentes')
    op.drop_table('produtos')
    op.drop_table('materia_prima_precos')
    op.drop_table('nota_itens')
    op.drop_table('notas')
    op.drop_table('materias_primas')
    op.drop_table('fornecedores')
    op.drop_table('unidades')
    op.drop_table('audit_logs')
    op.drop_table('users')
    
    # Drop enum types
    op.execute('DROP TYPE IF EXISTS statusnota')
    op.execute('DROP TYPE IF EXISTS origempreco')
    op.execute('DROP TYPE IF EXISTS auditaction')
    op.execute('DROP TYPE IF EXISTS userrole') 