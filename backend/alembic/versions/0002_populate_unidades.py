"""Populate unidades padrão

Revision ID: 0002
Revises: 0001
Create Date: 2025-01-27 10:01:00.000000

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Inserir unidades base primeiro (sem menor_unidade_id)
    op.execute("""
        INSERT INTO unidades (codigo, descricao, fator_para_menor, menor_unidade_id, is_base) 
        VALUES 
        ('kg', 'Quilograma', NULL, NULL, TRUE),
        ('m', 'Metro', NULL, NULL, TRUE),
        ('un', 'Unidade', NULL, NULL, TRUE),
        ('l', 'Litro', NULL, NULL, TRUE)
    """)
    
    # Atualizar as unidades base para apontarem para elas mesmas
    op.execute("""
        UPDATE unidades SET menor_unidade_id = id WHERE codigo = 'kg';
        UPDATE unidades SET menor_unidade_id = id WHERE codigo = 'm';
        UPDATE unidades SET menor_unidade_id = id WHERE codigo = 'un';
        UPDATE unidades SET menor_unidade_id = id WHERE codigo = 'l';
    """)
    
    # Inserir unidades derivadas apontando para as unidades base
    op.execute("""
        INSERT INTO unidades (codigo, descricao, fator_para_menor, menor_unidade_id, is_base) 
        VALUES 
        ('Rolo', 'Rolo', 1.0, (SELECT id FROM unidades WHERE codigo = 'm'), FALSE),
        ('Cadarço', 'Cadarço', 1.0, (SELECT id FROM unidades WHERE codigo = 'm'), FALSE),
        ('Fita', 'Fita Adesiva', 1.0, (SELECT id FROM unidades WHERE codigo = 'm'), FALSE),
        ('Jogo', 'Jogo', 1.0, (SELECT id FROM unidades WHERE codigo = 'un'), FALSE),
        ('Peça', 'Peça', 1.0, (SELECT id FROM unidades WHERE codigo = 'un'), FALSE)
    """)


def downgrade() -> None:
    # Remove unidades inseridas
    op.execute("DELETE FROM unidades WHERE codigo IN ('kg', 'm', 'un', 'l', 'Rolo', 'Cadarço', 'Fita', 'Jogo', 'Peça')") 