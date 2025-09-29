#!/usr/bin/env python3
"""
Script para deletar uma nota fiscal específica e seus dados relacionados
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Configuração do banco
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/nfe_system"

def deletar_nota_fiscal(nota_id):
    """Deleta uma nota fiscal e todos os dados relacionados"""
    
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        print(f"Buscando nota fiscal ID: {nota_id}")
        
        # Verificar se a nota existe
        result = session.execute(text("SELECT id, numero, created_at FROM notas WHERE id = :nota_id"), 
                               {"nota_id": nota_id})
        nota = result.fetchone()
        
        if not nota:
            print(f"ERRO: Nota fiscal ID {nota_id} nao encontrada!")
            return False
        
        print(f"Nota encontrada: {nota.numero} (criada em: {nota.created_at})")
        
        # 1. Deletar preços de matéria-prima vinculados à nota
        print("Deletando precos de materia-prima...")
        session.execute(text("DELETE FROM materia_prima_precos WHERE nota_id = :nota_id"), 
                       {"nota_id": nota_id})
        
        # 2. Deletar itens da nota
        print("Deletando itens da nota...")
        session.execute(text("DELETE FROM nota_itens WHERE nota_id = :nota_id"), 
                       {"nota_id": nota_id})
        
        # 3. Deletar a nota
        print("Deletando nota fiscal...")
        session.execute(text("DELETE FROM notas WHERE id = :nota_id"), 
                       {"nota_id": nota_id})
        
        # Confirmar as alterações
        session.commit()
        
        print(f"SUCESSO: Nota fiscal ID {nota_id} deletada com sucesso!")
        return True
        
    except Exception as e:
        session.rollback()
        print(f"ERRO ao deletar nota: {e}")
        return False
    
    finally:
        session.close()

def listar_notas_recentes():
    """Lista as notas mais recentes para facilitar a identificação"""
    
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        print("Notas fiscais mais recentes:")
        print("-" * 80)
        
        result = session.execute(text("""
            SELECT id, numero, created_at, valor_total 
            FROM notas 
            ORDER BY created_at DESC 
            LIMIT 10
        """))
        
        notas = result.fetchall()
        
        for nota in notas:
            print(f"ID: {nota.id:3d} | Numero: {nota.numero:15s} | Data: {nota.created_at} | Valor: R$ {nota.valor_total}")
        
        print("-" * 80)
        
    except Exception as e:
        print(f"ERRO ao listar notas: {e}")
    
    finally:
        session.close()

if __name__ == "__main__":
    print("DELETAR NOTA FISCAL DE TESTE")
    print("=" * 50)
    
    # Listar notas recentes
    listar_notas_recentes()
    
    # Solicitar ID da nota
    try:
        nota_id = input("\nDigite o ID da nota fiscal que deseja deletar: ").strip()
        
        if not nota_id.isdigit():
            print("ERRO: ID deve ser um numero!")
            sys.exit(1)
        
        nota_id = int(nota_id)
        
        # Confirmar exclusão
        confirmacao = input(f"ATENCAO: Tem certeza que deseja deletar a nota ID {nota_id}? (s/N): ").strip().lower()
        
        if confirmacao in ['s', 'sim', 'y', 'yes']:
            sucesso = deletar_nota_fiscal(nota_id)
            if sucesso:
                print("\nSUCESSO: Nota deletada! Agora voce pode testar novamente.")
            else:
                print("\nERRO: Falha ao deletar a nota.")
        else:
            print("Operacao cancelada.")
    
    except KeyboardInterrupt:
        print("\nOperacao cancelada pelo usuario.")
    except Exception as e:
        print(f"ERRO: {e}")