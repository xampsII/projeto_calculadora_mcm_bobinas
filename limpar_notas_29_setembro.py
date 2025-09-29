#!/usr/bin/env python3
"""
Script para deletar todas as notas fiscais do dia 29/09/2025 e suas matérias-primas relacionadas
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Configuração do banco
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/nfe_system"

def limpar_notas_29_setembro():
    """Deleta todas as notas do dia 29/09 e suas matérias-primas relacionadas"""
    
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        print("LIMPANDO NOTAS FISCAIS DO DIA 29/09/2025")
        print("=" * 60)
        
        # 1. Contar quantas notas serão deletadas
        result = session.execute(text("""
            SELECT COUNT(*) as total 
            FROM notas 
            WHERE created_at::date = '2025-09-29'
        """))
        total_notas = result.fetchone().total
        print(f"Notas encontradas para deletar: {total_notas}")
        
        if total_notas == 0:
            print("Nenhuma nota encontrada para o dia 29/09/2025")
            return True
        
        # 2. Listar as notas que serão deletadas
        print("\nNotas que serao deletadas:")
        print("-" * 60)
        result = session.execute(text("""
            SELECT id, numero, created_at, valor_total 
            FROM notas 
            WHERE created_at::date = '2025-09-29'
            ORDER BY created_at DESC
        """))
        
        notas = result.fetchall()
        for nota in notas:
            print(f"ID: {nota.id:3d} | Numero: {nota.numero:15s} | Data: {nota.created_at} | Valor: R$ {nota.valor_total}")
        
        # 3. Contar matérias-primas que serão deletadas
        result = session.execute(text("""
            SELECT COUNT(DISTINCT mp.id) as total
            FROM materias_primas mp
            JOIN nota_itens ni ON mp.id = ni.materia_prima_id
            JOIN notas n ON ni.nota_id = n.id
            WHERE n.created_at::date = '2025-09-29'
        """))
        total_materias = result.fetchone().total
        print(f"\nMaterias-primas relacionadas: {total_materias}")
        
        # 4. Listar matérias-primas que serão deletadas
        if total_materias > 0:
            print("\nMaterias-primas que serao deletadas:")
            print("-" * 60)
            result = session.execute(text("""
                SELECT DISTINCT mp.id, mp.nome, mp.unidade_codigo
                FROM materias_primas mp
                JOIN nota_itens ni ON mp.id = ni.materia_prima_id
                JOIN notas n ON ni.nota_id = n.id
                WHERE n.created_at::date = '2025-09-29'
                ORDER BY mp.nome
            """))
            
            materias = result.fetchall()
            for materia in materias:
                print(f"ID: {materia.id:3d} | Nome: {materia.nome:30s} | Unidade: {materia.unidade_codigo}")
        
        # 5. Confirmar exclusão
        print("\n" + "=" * 60)
        confirmacao = input("ATENCAO: Esta operacao e IRREVERSIVEL! Deseja continuar? (s/N): ").strip().lower()
        
        if confirmacao not in ['s', 'sim', 'y', 'yes']:
            print("Operacao cancelada.")
            return False
        
        print("\nIniciando exclusao...")
        
        # 6. Deletar preços de matéria-prima vinculados às notas do dia 29/09
        print("1. Deletando precos de materia-prima...")
        result = session.execute(text("""
            DELETE FROM materia_prima_precos
            WHERE nota_id IN (SELECT id FROM notas WHERE created_at::date = '2025-09-29')
        """))
        print(f"   {result.rowcount} precos deletados")
        
        # 7. Deletar itens das notas
        print("2. Deletando itens das notas...")
        result = session.execute(text("""
            DELETE FROM nota_itens
            WHERE nota_id IN (SELECT id FROM notas WHERE created_at::date = '2025-09-29')
        """))
        print(f"   {result.rowcount} itens deletados")
        
        # 8. Deletar matérias-primas criadas apenas pelas notas do dia 29/09
        print("3. Deletando materias-primas relacionadas...")
        result = session.execute(text("""
            DELETE FROM materias_primas
            WHERE id IN (
                SELECT DISTINCT mp.id
                FROM materias_primas mp
                JOIN nota_itens ni ON mp.id = ni.materia_prima_id
                JOIN notas n ON ni.nota_id = n.id
                WHERE n.created_at::date = '2025-09-29'
                AND mp.id NOT IN (
                    SELECT DISTINCT materia_prima_id
                    FROM nota_itens ni2
                    JOIN notas n2 ON ni2.nota_id = n2.id
                    WHERE n2.created_at::date != '2025-09-29'
                    AND ni2.materia_prima_id IS NOT NULL
                )
            )
        """))
        print(f"   {result.rowcount} materias-primas deletadas")
        
        # 9. Deletar as notas fiscais
        print("4. Deletando notas fiscais...")
        result = session.execute(text("""
            DELETE FROM notas
            WHERE created_at::date = '2025-09-29'
        """))
        print(f"   {result.rowcount} notas deletadas")
        
        # Confirmar as alterações
        session.commit()
        
        print("\n" + "=" * 60)
        print("SUCESSO: Todas as notas do dia 29/09/2025 foram deletadas!")
        print("SUCESSO: Materias-primas relacionadas foram deletadas!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        session.rollback()
        print(f"ERRO ao deletar: {e}")
        return False
    
    finally:
        session.close()

def verificar_limpeza():
    """Verifica se a limpeza foi bem-sucedida"""
    
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        print("\nVERIFICANDO LIMPEZA...")
        print("-" * 40)
        
        # Verificar notas restantes do dia 29/09
        result = session.execute(text("""
            SELECT COUNT(*) as total 
            FROM notas 
            WHERE created_at::date = '2025-09-29'
        """))
        notas_restantes = result.fetchone().total
        print(f"Notas restantes do dia 29/09: {notas_restantes}")
        
        # Verificar total de notas
        result = session.execute(text("SELECT COUNT(*) as total FROM notas"))
        total_notas = result.fetchone().total
        print(f"Total de notas no sistema: {total_notas}")
        
        # Verificar total de matérias-primas
        result = session.execute(text("SELECT COUNT(*) as total FROM materias_primas"))
        total_materias = result.fetchone().total
        print(f"Total de materias-primas no sistema: {total_materias}")
        
        if notas_restantes == 0:
            print("\nSUCESSO: Limpeza concluida com sucesso!")
        else:
            print(f"\nATENCAO: Ainda existem {notas_restantes} notas do dia 29/09")
        
    except Exception as e:
        print(f"ERRO ao verificar: {e}")
    
    finally:
        session.close()

if __name__ == "__main__":
    print("LIMPEZA COMPLETA - NOTAS 29/09/2025")
    print("=" * 60)
    print("Este script ira deletar:")
    print("- Todas as notas fiscais criadas no dia 29/09/2025")
    print("- Todos os itens dessas notas")
    print("- Todos os precos de materia-prima vinculados")
    print("- Materias-primas que foram criadas APENAS por essas notas")
    print("=" * 60)
    
    try:
        sucesso = limpar_notas_29_setembro()
        
        if sucesso:
            verificar_limpeza()
            print("\nAgora voce pode testar novamente com uma nova nota fiscal!")
        else:
            print("\nFalha na operacao de limpeza.")
    
    except KeyboardInterrupt:
        print("\nOperacao cancelada pelo usuario.")
    except Exception as e:
        print(f"ERRO: {e}")
