"""Populate unidades padrão

Revision ID: 0002
Revises: 0001
Create Date: 2025-01-27 10:01:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import String, Boolean, Numeric


# revision identifiers, used by Alembic.
revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create table objects for data insertion
    unidades = table('unidades',
        column('codigo', String),
        column('descricao', String),
        column('fator_para_menor', Numeric),
        column('menor_unidade_codigo', String),
        column('is_base', Boolean)
    )
    
    # Insert unidades padrão conforme especificação
    op.bulk_insert(unidades, [
        # Unidades base (não convertem)
        {'codigo': 'kg', 'descricao': 'Quilograma', 'fator_para_menor': None, 'menor_unidade_codigo': 'kg', 'is_base': True},
        {'codigo': 'm', 'descricao': 'Metro', 'fator_para_menor': None, 'menor_unidade_codigo': 'm', 'is_base': True},
        {'codigo': 'un', 'descricao': 'Unidade', 'fator_para_menor': None, 'menor_unidade_codigo': 'un', 'is_base': True},
        {'codigo': 'l', 'descricao': 'Litro', 'fator_para_menor': None, 'menor_unidade_codigo': 'l', 'is_base': True},
        
        # Unidades que convertem para menor
        {'codigo': 'Rolo', 'descricao': 'Rolo', 'fator_para_menor': 1.0, 'menor_unidade_codigo': 'm', 'is_base': False},
        {'codigo': 'Cadarço', 'descricao': 'Cadarço', 'fator_para_menor': 1.0, 'menor_unidade_codigo': 'm', 'is_base': False},
        {'codigo': 'Fita', 'descricao': 'Fita Adesiva', 'fator_para_menor': 1.0, 'menor_unidade_codigo': 'm', 'is_base': False},
        {'codigo': 'Jogo', 'descricao': 'Jogo', 'fator_para_menor': 1.0, 'menor_unidade_codigo': 'un', 'is_base': False},
        {'codigo': 'Peça', 'descricao': 'Peça', 'fator_para_menor': 1.0, 'menor_unidade_codigo': 'un', 'is_base': False},
    ])


def downgrade() -> None:
    # Remove unidades inseridas
    op.execute("DELETE FROM unidades WHERE codigo IN ('kg', 'm', 'un', 'l', 'Rolo', 'Cadarço', 'Fita', 'Jogo', 'Peça')") 