from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import and_
from app.database import get_db
from app.models.produto_final import ProdutoFinal
from app.schemas.produto_final import ProdutoFinalCreate, ProdutoFinalUpdate, ProdutoFinalResponse, ProdutoFinalCreateResponse

produtos_finais_router = APIRouter(prefix="/produtos-finais", tags=["Produtos Finais"])

@produtos_finais_router.post("/", status_code=status.HTTP_201_CREATED)
async def criar_produto_final(
    produto: ProdutoFinalCreate, 
    db: Session = Depends(get_db)
):
    """Criar novo produto final"""
    try:
        # Converter componentes para dicionários
        componentes_dict = [comp.model_dump() for comp in produto.componentes]
        
        # Criar produto final
        db_produto = ProdutoFinal(
            nome=produto.nome,
            id_unico=produto.idUnico,
            componentes=componentes_dict,
            ativo=produto.ativo
        )
        
        db.add(db_produto)
        db.commit()
        db.refresh(db_produto)
        
        return {
            "success": True,
            "message": "Produto final criado com sucesso!",
            "data": {
                "id": db_produto.id,
                "nome": db_produto.nome,
                "idUnico": db_produto.id_unico,
                "componentes": db_produto.componentes,
                "ativo": db_produto.ativo,
                "created_at": db_produto.created_at.isoformat() if db_produto.created_at else None,
                "updated_at": db_produto.updated_at.isoformat() if db_produto.updated_at else None
            }
        }
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "message": f"Erro ao criar produto final: {str(e)}"
        }

@produtos_finais_router.get("/materias-primas-disponiveis")
async def listar_materias_primas_disponiveis(
    db: Session = Depends(get_db)
):
    """Lista matérias-primas disponíveis para uso em produtos (endpoint público)"""
    try:
        from app.models.materia_prima import MateriaPrima
        from sqlalchemy import text
        
        # Função para converter preço para unidade base
        def converter_preco_para_unidade_base(preco_total, unidade_original, quantidade_original):
            """Converte preço para unidade base (ex: R$ 18 por 18L -> R$ 1 por L)"""
            if quantidade_original and quantidade_original > 0:
                return preco_total / quantidade_original
            return preco_total
        
        # Buscar todas as matérias-primas ativas
        materias_primas = db.query(MateriaPrima).filter(MateriaPrima.is_active == True).all()
        
        # Usar um dicionário para agrupar por nome e manter apenas o mais recente
        materias_unicas = {}
        
        for mp in materias_primas:
            # Buscar preço atual usando a view
            preco_query = text("""
                SELECT valor_unitario 
                FROM materia_prima_precos  
                WHERE materia_prima_id = :materia_id 
                AND (vigente_ate IS NULL OR vigente_ate > NOW())
                ORDER BY vigente_desde DESC 
                LIMIT 1
            """)
            
            result = db.execute(preco_query, {"materia_id": mp.id}).fetchone()
            preco_atual = float(result[0]) if result else 0.0
            
            # Extrair quantidade do nome se existir (ex: "VERNIZ 18L" -> quantidade=18)
            quantidade_original = 1
            nome_limpo = mp.nome
            unidade_original = mp.unidade_codigo or "un"
            
            # Procurar por padrões como "18L", "5KG", "10PC", etc.
            import re
            match = re.search(r'(\d+(?:\.\d+)?)\s*(L|KG|PC|UN|MT|M)$', mp.nome.upper())
            if match:
                quantidade_original = float(match.group(1))
                unidade_original = match.group(2)
                # Remover quantidade do nome
                nome_limpo = re.sub(r'\s*\d+(?:\.\d+)?\s*(L|KG|PC|UN|MT|M)$', '', mp.nome).strip()
            
            # Converter preço para unidade base
            preco_por_unidade = converter_preco_para_unidade_base(preco_atual, unidade_original, quantidade_original)
            
            # Se já existe uma matéria-prima com este nome, manter a que tem preço mais alto (mais recente)
            if nome_limpo in materias_unicas:
                if preco_por_unidade > materias_unicas[nome_limpo]['valorUnitario']:
                    materias_unicas[nome_limpo] = {
                        "id": mp.id,
                        "nome": nome_limpo,  # Nome sem quantidade
                        "unidade": unidade_original,
                        "valorUnitario": preco_por_unidade
                    }
            else:
                materias_unicas[nome_limpo] = {
                    "id": mp.id,
                    "nome": nome_limpo,  # Nome sem quantidade
                    "unidade": unidade_original,
                    "valorUnitario": preco_por_unidade
                }
        
        # Converter para lista e ordenar por nome
        materias_formatadas = list(materias_unicas.values())
        materias_formatadas.sort(key=lambda x: x['nome'])
        
        return materias_formatadas
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar matérias-primas: {str(e)}"
        )

@produtos_finais_router.get("/materia-prima/{materia_prima_id}/historico")
async def get_historico_precos_simples(
    materia_prima_id: int,
    db: Session = Depends(get_db)
):
    """Retorna o histórico completo de preços de uma matéria-prima com variações"""
    try:
        from app.models.materia_prima import MateriaPrima, MateriaPrimaPreco
        
        # Verificar se a matéria-prima existe
        materia_prima = db.query(MateriaPrima).filter(
            MateriaPrima.id == materia_prima_id
        ).first()
        
        if not materia_prima:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Matéria-prima não encontrada"
            )
        
        # Buscar histórico de preços ordenado por data (mais recente primeiro)
        precos = db.query(MateriaPrimaPreco).filter(
            MateriaPrimaPreco.materia_prima_id == materia_prima_id
        ).order_by(MateriaPrimaPreco.vigente_desde.desc()).all()
        
        historico = []
        preco_anterior = None
        
        for i, preco in enumerate(precos):
            # Calcular variação em relação ao preço anterior
            variacao_valor = None
            variacao_percentual = None
            
            if preco_anterior is not None:
                variacao_valor = float(preco.valor_unitario) - float(preco_anterior.valor_unitario)
                if float(preco_anterior.valor_unitario) > 0:
                    variacao_percentual = (variacao_valor / float(preco_anterior.valor_unitario)) * 100
            
            # Determinar status do preço
            status_preco = "Atual" if preco.vigente_ate is None else "Histórico"
            
            # Determinar origem do preço
            origem = "Manual"
            if preco.nota_id:
                origem = "Nota Fiscal"
            elif preco.fornecedor_id:
                origem = "Fornecedor"
            
            historico.append({
                "id": preco.id,
                "valor_unitario": float(preco.valor_unitario),
                "moeda": preco.moeda,
                "vigente_desde": preco.vigente_desde.isoformat() if preco.vigente_desde else None,
                "vigente_ate": preco.vigente_ate.isoformat() if preco.vigente_ate else None,
                "status": status_preco,
                "origem": origem,
                "fornecedor_id": preco.fornecedor_id,
                "nota_id": preco.nota_id,
                "observacao": getattr(preco, 'observacao', None),
                "created_at": preco.created_at.isoformat() if preco.created_at else None,
                "variacao": {
                    "valor": round(variacao_valor, 4) if variacao_valor is not None else None,
                    "percentual": round(variacao_percentual, 2) if variacao_percentual is not None else None,
                    "tendencia": "alta" if variacao_valor and variacao_valor > 0 else "baixa" if variacao_valor and variacao_valor < 0 else "estável"
                }
            })
            
            preco_anterior = preco
        
        # Calcular estatísticas gerais
        if len(historico) > 1:
            preco_atual = historico[0]["valor_unitario"]
            preco_mais_antigo = historico[-1]["valor_unitario"]
            variacao_total = preco_atual - preco_mais_antigo
            variacao_total_percentual = (variacao_total / preco_mais_antigo) * 100 if preco_mais_antigo > 0 else 0
            
            estatisticas = {
                "preco_atual": preco_atual,
                "preco_mais_antigo": preco_mais_antigo,
                "variacao_total": round(variacao_total, 4),
                "variacao_total_percentual": round(variacao_total_percentual, 2),
                "total_atualizacoes": len(historico),
                "periodo_dias": None
            }
            
            # Calcular período em dias
            if historico[0]["vigente_desde"] and historico[-1]["vigente_desde"]:
                from datetime import datetime
                data_inicio = datetime.fromisoformat(historico[-1]["vigente_desde"].replace('Z', '+00:00'))
                data_fim = datetime.fromisoformat(historico[0]["vigente_desde"].replace('Z', '+00:00'))
                estatisticas["periodo_dias"] = (data_fim - data_inicio).days
        else:
            estatisticas = {
                "preco_atual": historico[0]["valor_unitario"] if historico else None,
                "total_atualizacoes": len(historico)
            }
        
        return {
            "materia_prima": {
                "id": materia_prima.id,
                "nome": materia_prima.nome,
                "unidade": materia_prima.unidade_codigo
            },
            "historico": historico,
            "estatisticas": estatisticas,
            "total_registros": len(historico)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar histórico: {str(e)}"
        )

@produtos_finais_router.post("/materia-prima/{materia_prima_id}/atualizar-preco")
async def atualizar_preco_materia_prima(
    materia_prima_id: int,
    novo_preco: float,
    observacao: str = None,
    db: Session = Depends(get_db)
):
    """Atualiza o preço de uma matéria-prima manualmente, mantendo histórico"""
    try:
        from app.models.materia_prima import MateriaPrima, MateriaPrimaPreco
        from datetime import datetime
        
        # Verificar se a matéria-prima existe
        materia_prima = db.query(MateriaPrima).filter(
            MateriaPrima.id == materia_prima_id
        ).first()
        
        if not materia_prima:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Matéria-prima não encontrada"
            )
        
        # Buscar preço atual
        preco_atual = db.query(MateriaPrimaPreco).filter(
            and_(
                MateriaPrimaPreco.materia_prima_id == materia_prima_id,
                MateriaPrimaPreco.vigente_ate.is_(None)
            )
        ).first()
        
        # Fechar preço atual se existir
        if preco_atual:
            preco_atual.vigente_ate = datetime.now()
            db.add(preco_atual)
        
        # Criar novo preço
        novo_preco_obj = MateriaPrimaPreco(
            materia_prima_id=materia_prima_id,
            valor_unitario=novo_preco,
            vigente_desde=datetime.now(),
            vigente_ate=None,  # Preço atual
            fornecedor_id=None,  # Atualização manual
            nota_id=None,  # Atualização manual
            observacao=observacao
        )
        
        db.add(novo_preco_obj)
        db.commit()
        
        return {
            "success": True,
            "message": f"Preço da matéria-prima '{materia_prima.nome}' atualizado para R$ {novo_preco:.2f}",
            "materia_prima": {
                "id": materia_prima.id,
                "nome": materia_prima.nome,
                "preco_anterior": float(preco_atual.valor_unitario) if preco_atual else None,
                "preco_novo": novo_preco,
                "variacao": novo_preco - float(preco_atual.valor_unitario) if preco_atual else None
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar preço: {str(e)}"
        )

@produtos_finais_router.post("/{produto_id}/atualizar-preco")
async def atualizar_preco_produto_final(
    produto_id: int,
    novo_custo: float,
    observacao: str = None,
    db: Session = Depends(get_db)
):
    """Atualiza o preço de um produto final manualmente, mantendo histórico"""
    try:
        from app.models.produto_final import ProdutoFinal
        from app.models.produto import ProdutoPreco
        from datetime import datetime
        
        # Verificar se o produto existe
        produto = db.query(ProdutoFinal).filter(
            ProdutoFinal.id == produto_id
        ).first()
        
        if not produto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produto final não encontrado"
            )
        
        # Buscar preço atual do produto
        preco_atual = db.query(ProdutoPreco).filter(
            and_(
                ProdutoPreco.produto_id == produto_id,
                ProdutoPreco.vigente_ate.is_(None)
            )
        ).first()
        
        # Fechar preço atual se existir
        if preco_atual:
            preco_atual.vigente_ate = datetime.now()
            db.add(preco_atual)
        
        # Criar novo preço
        novo_preco_obj = ProdutoPreco(
            produto_id=produto_id,
            custo_total=novo_custo,
            vigente_desde=datetime.now(),
            vigente_ate=None,  # Preço atual
            observacao=observacao
        )
        
        db.add(novo_preco_obj)
        db.commit()
        
        return {
            "success": True,
            "message": f"Preço do produto '{produto.nome}' atualizado para R$ {novo_custo:.2f}",
            "produto": {
                "id": produto.id,
                "nome": produto.nome,
                "custo_anterior": float(preco_atual.custo_total) if preco_atual else None,
                "custo_novo": novo_custo,
                "variacao": novo_custo - float(preco_atual.custo_total) if preco_atual else None
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar preço do produto: {str(e)}"
        )

@produtos_finais_router.get("/{produto_id}/historico-precos")
async def get_historico_precos_produto(
    produto_id: int,
    db: Session = Depends(get_db)
):
    """Retorna o histórico de preços de um produto final"""
    try:
        from app.models.produto_final import ProdutoFinal
        from app.models.produto import ProdutoPreco
        
        # Verificar se o produto existe
        produto = db.query(ProdutoFinal).filter(
            ProdutoFinal.id == produto_id
        ).first()
        
        if not produto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produto final não encontrado"
            )
        
        # Buscar histórico de preços
        precos = db.query(ProdutoPreco).filter(
            ProdutoPreco.produto_id == produto_id
        ).order_by(ProdutoPreco.vigente_desde.desc()).all()
        
        historico = []
        for preco in precos:
            historico.append({
                "id": preco.id,
                "custo_total": float(preco.custo_total),
                "vigente_desde": preco.vigente_desde.isoformat() if preco.vigente_desde else None,
                "vigente_ate": preco.vigente_ate.isoformat() if preco.vigente_ate else None,
                "observacao": getattr(preco, 'observacao', None),
                "created_at": preco.created_at.isoformat() if preco.created_at else None
            })
        
        return {
            "produto": {
                "id": produto.id,
                "nome": produto.nome,
                "id_unico": produto.id_unico
            },
            "historico": historico,
            "total_precos": len(historico)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar histórico do produto: {str(e)}"
        )

@produtos_finais_router.post("/teste-atualizar-preco")
async def teste_atualizar_preco(
    materia_prima_id: int,
    novo_preco: float,
    db: Session = Depends(get_db)
):
    """Endpoint de teste para atualizar preço"""
    try:
        from app.models.materia_prima import MateriaPrima, MateriaPrimaPreco
        from datetime import datetime
        
        # Verificar se a matéria-prima existe
        materia_prima = db.query(MateriaPrima).filter(
            MateriaPrima.id == materia_prima_id
        ).first()
        
        if not materia_prima:
            return {"error": "Matéria-prima não encontrada"}
        
        # Buscar preço atual
        preco_atual = db.query(MateriaPrimaPreco).filter(
            MateriaPrimaPreco.materia_prima_id == materia_prima_id,
            MateriaPrimaPreco.vigente_ate.is_(None)
        ).first()
        
        return {
            "success": True,
            "materia_prima": materia_prima.nome,
            "preco_atual": float(preco_atual.valor_unitario) if preco_atual else None,
            "novo_preco": novo_preco
        }
        
    except Exception as e:
        return {"error": str(e)}

@produtos_finais_router.get("/materia-prima/{materia_prima_id}/historico-simples")
async def get_historico_precos_simples_teste(
    materia_prima_id: int,
    db: Session = Depends(get_db)
):
    """Retorna o histórico de preços de uma matéria-prima (versão simples para teste)"""
    try:
        from app.models.materia_prima import MateriaPrima, MateriaPrimaPreco
        
        # Verificar se a matéria-prima existe
        materia_prima = db.query(MateriaPrima).filter(
            MateriaPrima.id == materia_prima_id
        ).first()
        
        if not materia_prima:
            raise HTTPException(
                status_code=404,
                detail="Matéria-prima não encontrada"
            )
        
        # Buscar histórico de preços ordenado por data (mais recente primeiro)
        precos = db.query(MateriaPrimaPreco).filter(
            MateriaPrimaPreco.materia_prima_id == materia_prima_id
        ).order_by(MateriaPrimaPreco.vigente_desde.desc()).all()
        
        historico = []
        preco_anterior = None
        
        for i, preco in enumerate(precos):
            # Calcular variação em relação ao preço anterior
            variacao_valor = None
            variacao_percentual = None
            
            if preco_anterior is not None:
                variacao_valor = float(preco.valor_unitario) - float(preco_anterior.valor_unitario)
                if float(preco_anterior.valor_unitario) > 0:
                    variacao_percentual = (variacao_valor / float(preco_anterior.valor_unitario)) * 100
            
            # Determinar status do preço
            status_preco = "Atual" if preco.vigente_ate is None else "Histórico"
            
            # Determinar origem do preço
            origem = "Manual"
            if preco.nota_id:
                origem = "Nota Fiscal"
            elif preco.fornecedor_id:
                origem = "Fornecedor"
            
            historico.append({
                "id": preco.id,
                "valor_unitario": float(preco.valor_unitario),
                "moeda": preco.moeda,
                "vigente_desde": preco.vigente_desde.isoformat() if preco.vigente_desde else None,
                "vigente_ate": preco.vigente_ate.isoformat() if preco.vigente_ate else None,
                "status": status_preco,
                "origem": origem,
                "fornecedor_id": preco.fornecedor_id,
                "nota_id": preco.nota_id,
                "created_at": preco.created_at.isoformat() if preco.created_at else None,
                "variacao": {
                    "valor": round(variacao_valor, 4) if variacao_valor is not None else None,
                    "percentual": round(variacao_percentual, 2) if variacao_percentual is not None else None,
                    "tendencia": "alta" if variacao_valor and variacao_valor > 0 else "baixa" if variacao_valor and variacao_valor < 0 else "estável"
                }
            })
            
            preco_anterior = preco
        
        # Calcular estatísticas gerais
        if len(historico) > 1:
            preco_atual = historico[0]["valor_unitario"]
            preco_mais_antigo = historico[-1]["valor_unitario"]
            variacao_total = preco_atual - preco_mais_antigo
            variacao_total_percentual = (variacao_total / preco_mais_antigo) * 100 if preco_mais_antigo > 0 else 0
            
            estatisticas = {
                "preco_atual": preco_atual,
                "preco_mais_antigo": preco_mais_antigo,
                "variacao_total": round(variacao_total, 4),
                "variacao_total_percentual": round(variacao_total_percentual, 2),
                "total_atualizacoes": len(historico),
                "periodo_dias": None
            }
            
            # Calcular período em dias
            if historico[0]["vigente_desde"] and historico[-1]["vigente_desde"]:
                from datetime import datetime
                data_inicio = datetime.fromisoformat(historico[-1]["vigente_desde"].replace('Z', '+00:00'))
                data_fim = datetime.fromisoformat(historico[0]["vigente_desde"].replace('Z', '+00:00'))
                estatisticas["periodo_dias"] = (data_fim - data_inicio).days
        else:
            estatisticas = {
                "preco_atual": historico[0]["valor_unitario"] if historico else None,
                "total_atualizacoes": len(historico)
            }
        
        return {
            "materia_prima": {
                "id": materia_prima.id,
                "nome": materia_prima.nome,
                "unidade": materia_prima.unidade_codigo
            },
            "historico": historico,
            "estatisticas": estatisticas,
            "total_registros": len(historico)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar histórico: {str(e)}"
        )

@produtos_finais_router.get("/")
async def listar_produtos_finais(
    skip: int = 0, 
    limit: int = 100, 
    ativo: bool = True,
    db: Session = Depends(get_db)
):
    """Listar produtos finais"""
    query = db.query(ProdutoFinal)
    if ativo is not None:
        query = query.filter(ProdutoFinal.ativo == ativo)
    
    produtos = query.offset(skip).limit(limit).all()
    
    # Converter manualmente para o formato esperado pelo frontend
    produtos_formatados = []
    for produto in produtos:
        # Calcular preço atual do produto usando a mesma lógica do frontend
        custo_total = 0.0
        try:
            from app.models.materia_prima import MateriaPrima
            from sqlalchemy import text
            
            # Função para converter preço para unidade base (mesma do frontend)
            def converter_preco_para_unidade_base(preco_total, unidade_original, quantidade_original):
                """Converte preço para unidade base (ex: R$ 18 por 18L -> R$ 1 por L)"""
                if quantidade_original and quantidade_original > 0:
                    return preco_total / quantidade_original
                return preco_total
            
            for componente in produto.componentes:
                # Buscar matéria-prima pelo nome exato primeiro
                materia_prima = db.query(MateriaPrima).filter(
                    MateriaPrima.nome == componente['materiaPrimaNome']
                ).first()
                
                # Se não encontrar, buscar por similaridade
                if not materia_prima:
                    materia_prima = db.query(MateriaPrima).filter(
                        MateriaPrima.nome.ilike(f"%{componente['materiaPrimaNome']}%")
                    ).first()
                
                if materia_prima:
                    # Buscar preço atual usando a tabela
                    preco_query = text("""
                        SELECT valor_unitario 
                        FROM materia_prima_precos 
                        WHERE materia_prima_id = :materia_id 
                        AND (vigente_ate IS NULL OR vigente_ate > NOW())
                        ORDER BY vigente_desde DESC 
                        LIMIT 1
                    """)
                    
                    result = db.execute(preco_query, {"materia_id": materia_prima.id}).fetchone()
                    
                    if result:
                        preco_atual = float(result[0])
                        
                        # Aplicar a mesma lógica de conversão do frontend
                        import re
                        quantidade_original = 1
                        nome_limpo = materia_prima.nome
                        unidade_original = materia_prima.unidade_codigo or "un"
                        
                        # Procurar por padrões como "18L", "5KG", "10PC", etc.
                        match = re.search(r'(\d+(?:\.\d+)?)\s*(L|KG|PC|UN|MT|M)$', materia_prima.nome.upper())
                        if match:
                            quantidade_original = float(match.group(1))
                            unidade_original = match.group(2)
                        
                        # Converter preço para unidade base
                        preco_por_unidade = converter_preco_para_unidade_base(preco_atual, unidade_original, quantidade_original)
                        
                        custo_total += componente['quantidade'] * preco_por_unidade
        except Exception as e:
            # Se houver erro no cálculo, usar 0
            custo_total = 0.0
        
        produtos_formatados.append({
            "id": produto.id,
            "nome": produto.nome,
            "idUnico": produto.id_unico,
            "componentes": produto.componentes,
            "ativo": produto.ativo,
            "custo_total": round(custo_total, 2),
            "created_at": produto.created_at.isoformat() if produto.created_at else None,
            "updated_at": produto.updated_at.isoformat() if produto.updated_at else None
        })
    
    return produtos_formatados

@produtos_finais_router.get("/{produto_id}/calcular-preco")
async def calcular_preco_produto(
    produto_id: int,
    margem_lucro: float = 0.0,
    db: Session = Depends(get_db)
):
    """Calcular preço atual do produto baseado nos preços atuais das matérias-primas"""
    produto = db.query(ProdutoFinal).filter(ProdutoFinal.id == produto_id).first()
    if not produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto final não encontrado"
        )
    
    try:
        # Buscar preços atuais das matérias-primas usando a mesma lógica do frontend
        from app.models.materia_prima import MateriaPrima
        from sqlalchemy import text
        
        # Função para converter preço para unidade base (mesma do frontend)
        def converter_preco_para_unidade_base(preco_total, unidade_original, quantidade_original):
            """Converte preço para unidade base (ex: R$ 18 por 18L -> R$ 1 por L)"""
            if quantidade_original and quantidade_original > 0:
                return preco_total / quantidade_original
            return preco_total
        
        custo_total = 0.0
        componentes_detalhados = []
        
        for componente in produto.componentes:
            # Buscar matéria-prima pelo nome exato primeiro
            materia_prima = db.query(MateriaPrima).filter(
                MateriaPrima.nome == componente['materiaPrimaNome']
            ).first()
            
            # Se não encontrar, buscar por similaridade
            if not materia_prima:
                materia_prima = db.query(MateriaPrima).filter(
                    MateriaPrima.nome.ilike(f"%{componente['materiaPrimaNome']}%")
                ).first()
            
            if materia_prima:
                # Buscar preço atual usando a tabela
                preco_query = text("""
                    SELECT valor_unitario 
                    FROM materia_prima_precos 
                    WHERE materia_prima_id = :materia_id 
                    AND (vigente_ate IS NULL OR vigente_ate > NOW())
                    ORDER BY vigente_desde DESC 
                    LIMIT 1
                """)
                
                result = db.execute(preco_query, {"materia_id": materia_prima.id}).fetchone()
                
                if result:
                    preco_atual = float(result[0])
                    
                    # Aplicar a mesma lógica de conversão do frontend
                    import re
                    quantidade_original = 1
                    nome_limpo = materia_prima.nome
                    unidade_original = materia_prima.unidade_codigo or "un"
                    
                    # Procurar por padrões como "18L", "5KG", "10PC", etc.
                    match = re.search(r'(\d+(?:\.\d+)?)\s*(L|KG|PC|UN|MT|M)$', materia_prima.nome.upper())
                    if match:
                        quantidade_original = float(match.group(1))
                        unidade_original = match.group(2)
                    
                    # Converter preço para unidade base
                    preco_por_unidade = converter_preco_para_unidade_base(preco_atual, unidade_original, quantidade_original)
                    
                    valor_componente = componente['quantidade'] * preco_por_unidade
                    custo_total += valor_componente
                    
                    componentes_detalhados.append({
                        "nome": componente['materiaPrimaNome'],
                        "quantidade": componente['quantidade'],
                        "unidade": componente['unidadeMedida'],
                        "preco_atual": preco_por_unidade,
                        "valor_total": valor_componente
                    })
                else:
                    # Se não há preço atual, usar valor 0
                    componentes_detalhados.append({
                        "nome": componente['materiaPrimaNome'],
                        "quantidade": componente['quantidade'],
                        "unidade": componente['unidadeMedida'],
                        "preco_atual": 0.0,
                        "valor_total": 0.0
                    })
        
        # Calcular preço de venda com margem
        margem_decimal = margem_lucro / 100
        preco_venda = custo_total * (1 + margem_decimal)
        margem_valor = preco_venda - custo_total
        
        return {
            "produto_id": produto.id,
            "produto_nome": produto.nome,
            "componentes": componentes_detalhados,
            "custo_total": round(custo_total, 2),
            "margem_lucro_percentual": margem_lucro,
            "margem_lucro_valor": round(margem_valor, 2),
            "preco_venda": round(preco_venda, 2),
            "atualizado_em": produto.updated_at.isoformat() if produto.updated_at else None
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao calcular preço: {str(e)}"
        )

@produtos_finais_router.get("/{produto_id}", response_model=ProdutoFinalResponse)
async def buscar_produto_final(
    produto_id: int, 
    db: Session = Depends(get_db)
):
    """Buscar produto final por ID"""
    produto = db.query(ProdutoFinal).filter(ProdutoFinal.id == produto_id).first()
    if not produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto final não encontrado"
        )
    return produto

@produtos_finais_router.put("/{produto_id}", response_model=ProdutoFinalResponse)
async def atualizar_produto_final(
    produto_id: int,
    produto: ProdutoFinalUpdate,
    db: Session = Depends(get_db)
):
    """Atualizar produto final com histórico de alterações"""
    db_produto = db.query(ProdutoFinal).filter(ProdutoFinal.id == produto_id).first()
    if not db_produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto final não encontrado"
        )
    
    try:
        # Calcular custo anterior para comparação
        custo_anterior = 0.0
        if db_produto.componentes:
            try:
                from app.models.materia_prima import MateriaPrima
                from sqlalchemy import text
                
                for componente in db_produto.componentes:
                    materia_prima = db.query(MateriaPrima).filter(
                        MateriaPrima.nome == componente['materiaPrimaNome']
                    ).first()
                    
                    if materia_prima:
                        preco_query = text("""
                            SELECT valor_unitario 
                            FROM materia_prima_precos 
                            WHERE materia_prima_id = :materia_id 
                            AND (vigente_ate IS NULL OR vigente_ate > NOW())
                            ORDER BY vigente_desde DESC 
                            LIMIT 1
                        """)
                        
                        result = db.execute(preco_query, {"materia_id": materia_prima.id}).fetchone()
                        if result:
                            preco_atual = float(result[0])
                            custo_anterior += componente['quantidade'] * preco_atual
            except:
                pass
        
        # Atualizar campos
        if produto.nome:
            db_produto.nome = produto.nome
        if produto.idUnico:
            db_produto.id_unico = produto.idUnico
        if produto.componentes:
            componentes_dict = [comp.model_dump() for comp in produto.componentes]
            db_produto.componentes = componentes_dict
        if produto.ativo is not None:
            db_produto.ativo = produto.ativo
        
        # Calcular novo custo
        custo_novo = 0.0
        if produto.componentes:
            try:
                from app.models.materia_prima import MateriaPrima
                from sqlalchemy import text
                
                for componente in produto.componentes:
                    materia_prima = db.query(MateriaPrima).filter(
                        MateriaPrima.nome == componente.materiaPrimaNome
                    ).first()
                    
                    if materia_prima:
                        preco_query = text("""
                            SELECT valor_unitario 
                            FROM materia_prima_precos 
                            WHERE materia_prima_id = :materia_id 
                            AND (vigente_ate IS NULL OR vigente_ate > NOW())
                            ORDER BY vigente_desde DESC 
                            LIMIT 1
                        """)
                        
                        result = db.execute(preco_query, {"materia_id": materia_prima.id}).fetchone()
                        if result:
                            preco_atual = float(result[0])
                            custo_novo += componente.quantidade * preco_atual
            except:
                pass
        
        # TODO: Implementar histórico de alterações quando a tabela produto_precos estiver criada
        # Por enquanto, apenas log da variação
        if abs(custo_novo - custo_anterior) > 0.01:
            print(f"Variação de custo detectada: R$ {custo_anterior:.2f} -> R$ {custo_novo:.2f} (Δ: R$ {custo_novo - custo_anterior:.2f})")
        
        db.commit()
        db.refresh(db_produto)
        return db_produto
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar produto final: {str(e)}"
        )

@produtos_finais_router.delete("/{produto_id}")
async def deletar_produto_final(
    produto_id: int,
    db: Session = Depends(get_db)
):
    """Deletar produto final (soft delete)"""
    db_produto = db.query(ProdutoFinal).filter(ProdutoFinal.id == produto_id).first()
    if not db_produto:
        return {
            "success": False,
            "message": "Produto final não encontrado"
        }
    
    try:
        # Soft delete
        db_produto.ativo = False
        db.commit()
        return {
            "success": True,
            "message": "Produto final excluído com sucesso!"
        }
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "message": f"Erro ao excluir produto final: {str(e)}"
        }



