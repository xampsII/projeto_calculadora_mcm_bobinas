"""
Arquivo de seeds para popular o banco de dados com dados iniciais
"""
from dotenv import load_dotenv
load_dotenv()

from app.database import SessionLocal
from app.models.user import User
from app.models.unidade import Unidade
from app.models.fornecedor import Fornecedor
from app.models.materia_prima import MateriaPrima
from app.models.materia_prima import MateriaPrimaPreco
from app.models.produto import Produto, ProdutoComponente, ProdutoPreco
from app.models.enums import UserRole
from app.auth.jwt import get_password_hash
from datetime import datetime, date
from decimal import Decimal


def criar_usuarios():
    """Cria usuários iniciais"""
    db = SessionLocal()
    
    try:
        # Verificar se já existem usuários
        if db.query(User).count() > 0:
            print("Usuários já existem, pulando criação...")
            return
        
        # Usuário admin
        admin_user = User(
            name="Administrador",
            email="admin@nfe.com",
            password_hash=get_password_hash("admin123"),
            role=UserRole.admin,
            is_active=True
        )
        db.add(admin_user)
        
        # Usuário editor
        editor_user = User(
            name="Editor",
            email="editor@nfe.com",
            password_hash=get_password_hash("editor123"),
            role=UserRole.editor,
            is_active=True
        )
        db.add(editor_user)
        
        # Usuário viewer
        viewer_user = User(
            name="Visualizador",
            email="viewer@nfe.com",
            password_hash=get_password_hash("viewer123"),
            role=UserRole.viewer,
            is_active=True
        )
        db.add(viewer_user)
        
        db.commit()
        print("Usuários criados com sucesso!")
        
    except Exception as e:
        print(f"Erro ao criar usuários: {e}")
        db.rollback()
    finally:
        db.close()


def criar_unidades():
    """Cria unidades de medida padrão"""
    db = SessionLocal()
    
    try:
        # Verificar se já existem unidades
        if db.query(Unidade).count() > 0:
            print("Unidades já existem, pulando criação...")
            return
        
        # Unidades base
        unidades_base = [
            Unidade(codigo="kg", descricao="Quilograma", fator_para_menor=1.0, menor_unidade_codigo="kg", is_base=True),
            Unidade(codigo="m", descricao="Metro", fator_para_menor=1.0, menor_unidade_codigo="m", is_base=True),
            Unidade(codigo="un", descricao="Unidade", fator_para_menor=1.0, menor_unidade_codigo="un", is_base=True),
            Unidade(codigo="l", descricao="Litro", fator_para_menor=1.0, menor_unidade_codigo="l", is_base=True),
        ]
        
        for unidade in unidades_base:
            db.add(unidade)
        
        # Unidades conversíveis
        unidades_conversiveis = [
            Unidade(codigo="Rolo", descricao="Rolo", fator_para_menor=10.0, menor_unidade_codigo="m", is_base=False),
            Unidade(codigo="Cadarço", descricao="Cadarço", fator_para_menor=1.0, menor_unidade_codigo="m", is_base=False),
            Unidade(codigo="Fita", descricao="Fita Adesiva", fator_para_menor=1.0, menor_unidade_codigo="m", is_base=False),
            Unidade(codigo="Jogo", descricao="Jogo", fator_para_menor=1.0, menor_unidade_codigo="un", is_base=False),
            Unidade(codigo="Peça", descricao="Peça", fator_para_menor=1.0, menor_unidade_codigo="un", is_base=False),
        ]
        
        for unidade in unidades_conversiveis:
            db.add(unidade)
        
        db.commit()
        print("Unidades criadas com sucesso!")
        
    except Exception as e:
        print(f"Erro ao criar unidades: {e}")
        db.rollback()
    finally:
        db.close()


def criar_fornecedores():
    """Cria fornecedores de exemplo"""
    db = SessionLocal()
    
    try:
        # Verificar se já existem fornecedores
        if db.query(Fornecedor).count() > 0:
            print("Fornecedores já existem, pulando criação...")
            return
        
        fornecedores = [
            Fornecedor(
                cnpj="12345678000195",
                nome="Fornecedor A LTDA",
                endereco="Rua A, 123 - São Paulo/SP"
            ),
            Fornecedor(
                cnpj="98765432000187",
                nome="Fornecedor B S/A",
                endereco="Av. B, 456 - Rio de Janeiro/RJ"
            ),
            Fornecedor(
                cnpj="45678912000134",
                nome="Fornecedor C ME",
                endereco="Rua C, 789 - Belo Horizonte/MG"
            ),
        ]
        
        for fornecedor in fornecedores:
            db.add(fornecedor)
        
        db.commit()
        print("Fornecedores criados com sucesso!")
        
    except Exception as e:
        print(f"Erro ao criar fornecedores: {e}")
        db.rollback()
    finally:
        db.close()


def criar_materias_primas():
    """Cria matérias-primas de exemplo"""
    db = SessionLocal()
    
    try:
        # Verificar se já existem matérias-primas
        if db.query(MateriaPrima).count() > 0:
            print("Matérias-primas já existem, pulando criação...")
            return
        
        # Buscar fornecedor para associar
        fornecedor = db.query(Fornecedor).first()
        if not fornecedor:
            print("Nenhum fornecedor encontrado, criando matérias-primas sem fornecedor...")
            fornecedor_id = None
        else:
            fornecedor_id = fornecedor.id
        
        # Buscar unidades
        unidade_kg = db.query(Unidade).filter(Unidade.codigo == "kg").first()
        unidade_m = db.query(Unidade).filter(Unidade.codigo == "m").first()
        unidade_un = db.query(Unidade).filter(Unidade.codigo == "un").first()
        
        if not all([unidade_kg, unidade_m, unidade_un]):
            print("Unidades não encontradas, pulando criação de matérias-primas...")
            return
        
        # Criar matérias-primas
        materias_primas = [
            MateriaPrima(
                nome="Borracha Natural",
                unidade_codigo="kg",
                menor_unidade_codigo="kg"
            ),
            MateriaPrima(
                nome="Cadarço 10mm",
                unidade_codigo="m",
                menor_unidade_codigo="m"
            ),
            MateriaPrima(
                nome="Fita Adesiva",
                unidade_codigo="m",
                menor_unidade_codigo="m"
            ),
            MateriaPrima(
                nome="Tecido Algodão",
                unidade_codigo="m",
                menor_unidade_codigo="m"
            ),
        ]
        
        for mp in materias_primas:
            db.add(mp)
        
        db.commit()
        
        # Criar preços iniciais
        precos = [
            MateriaPrimaPreco(
                materia_prima_id=1,  # Borracha Natural
                valor_unitario=Decimal("18.90"),
                vigente_desde=date.today(),
                fornecedor_id=fornecedor_id
            ),
            MateriaPrimaPreco(
                materia_prima_id=2,  # Cadarço 10mm
                valor_unitario=Decimal("2.35"),
                vigente_desde=date.today(),
                fornecedor_id=fornecedor_id
            ),
            MateriaPrimaPreco(
                materia_prima_id=3,  # Fita Adesiva
                valor_unitario=Decimal("0.85"),
                vigente_desde=date.today(),
                fornecedor_id=fornecedor_id
            ),
            MateriaPrimaPreco(
                materia_prima_id=4,  # Tecido Algodão
                valor_unitario=Decimal("12.50"),
                vigente_desde=date.today(),
                fornecedor_id=fornecedor_id
            ),
        ]
        
        for preco in precos:
            db.add(preco)
        
        db.commit()
        print("Matérias-primas e preços criados com sucesso!")
        
    except Exception as e:
        print(f"Erro ao criar matérias-primas: {e}")
        db.rollback()
    finally:
        db.close()


def criar_produtos():
    """Cria produtos de exemplo"""
    db = SessionLocal()
    
    try:
        # Verificar se já existem produtos
        if db.query(Produto).count() > 0:
            print("Produtos já existem, pulando criação...")
            return
        
        # Criar produtos
        produtos = [
            Produto(nome="Tênis Modelo X"),
            Produto(nome="Sapato Social"),
            Produto(nome="Mochila Escolar"),
        ]
        
        for produto in produtos:
            db.add(produto)
        
        db.commit()
        
        # Criar componentes dos produtos
        componentes = [
            # Tênis Modelo X
            ProdutoComponente(
                produto_id=1,
                materia_prima_id=1,  # Borracha Natural
                quantidade=Decimal("0.05"),
                unidade_codigo="kg"
            ),
            ProdutoComponente(
                produto_id=1,
                materia_prima_id=2,  # Cadarço 10mm
                quantidade=Decimal("1.2"),
                unidade_codigo="m"
            ),
            ProdutoComponente(
                produto_id=1,
                materia_prima_id=3,  # Fita Adesiva
                quantidade=Decimal("0.3"),
                unidade_codigo="m"
            ),
            
            # Sapato Social
            ProdutoComponente(
                produto_id=2,
                materia_prima_id=4,  # Tecido Algodão
                quantidade=Decimal("0.8"),
                unidade_codigo="m"
            ),
            ProdutoComponente(
                produto_id=2,
                materia_prima_id=3,  # Fita Adesiva
                quantidade=Decimal("0.2"),
                unidade_codigo="m"
            ),
            
            # Mochila Escolar
            ProdutoComponente(
                produto_id=3,
                materia_prima_id=4,  # Tecido Algodão
                quantidade=Decimal("1.5"),
                unidade_codigo="m"
            ),
            ProdutoComponente(
                produto_id=3,
                materia_prima_id=3,  # Fita Adesiva
                quantidade=Decimal("0.5"),
                unidade_codigo="m"
            ),
        ]
        
        for componente in componentes:
            db.add(componente)
        
        db.commit()
        
        # Calcular e criar preços dos produtos
        for produto in produtos:
            # Buscar componentes
            comps = db.query(ProdutoComponente).filter(
                ProdutoComponente.produto_id == produto.id
            ).all()
            
            if comps:
                custo_total = Decimal("0")
                
                for comp in comps:
                    # Buscar preço atual da matéria-prima
                    preco_mp = db.query(MateriaPrimaPreco).filter(
                        MateriaPrimaPreco.materia_prima_id == comp.materia_prima_id,
                        MateriaPrimaPreco.vigente_ate.is_(None)
                    ).first()
                    
                    if preco_mp:
                        custo_total += comp.quantidade * preco_mp.valor_unitario
                
                if custo_total > 0:
                    preco_produto = ProdutoPreco(
                        produto_id=produto.id,
                        custo_total=custo_total,
                        vigente_desde=date.today()
                    )
                    db.add(preco_produto)
        
        db.commit()
        print("Produtos, componentes e preços criados com sucesso!")
        
    except Exception as e:
        print(f"Erro ao criar produtos: {e}")
        db.rollback()
    finally:
        db.close()


def executar_seeds():
    """Executa todos os seeds"""
    print("Iniciando execução dos seeds...")
    errors = []

    try:
        criar_usuarios()
        print("Usuários criados com sucesso!")
    except Exception as e:
        errors.append(("usuarios", e))

    try:
        criar_unidades()
        print("Unidades criadas com sucesso!")
    except Exception as e:
        errors.append(("unidades", e))

    try:
        criar_fornecedores()
        print("Fornecedores criados com sucesso!")
    except Exception as e:
        errors.append(("fornecedores", e))

    try:
        criar_materias_primas()
        print("Matérias-primas criadas com sucesso!")
    except Exception as e:
        errors.append(("materias_primas", e))

    try:
        criar_produtos()
        print("Produtos criados com sucesso!")
    except Exception as e:
        errors.append(("produtos", e))

    if errors:
        for where, err in errors:
            print(f"❌ Erro em {where}: {err}")
        raise SystemExit(1)

    print("✅ Seeds executados com sucesso!")


if __name__ == "__main__":
    import sys
    
    success = executar_seeds()
    if not success:
        sys.exit(1)
    sys.exit(0) 