from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from datetime import datetime, date
import hashlib
import os
import logging
from lxml import etree

from app.database import get_db
from app.models.user import User
from app.models.nota import Nota, NotaItem
from app.models.enums import StatusNota
from app.models.fornecedor import Fornecedor
from app.models.materia_prima import MateriaPrima, MateriaPrimaPreco
from app.models.unidade import Unidade
from app.schemas.nota import (
    NotaCreate,
    NotaUpdate,
    NotaItemCreate,
    NotaResponse,
    NotaItemResponse,
    NotaFilters
)
from app.schemas.pagination import PaginatedResponse
from app.auth.dependencies import get_current_active_user, require_editor
from app.config import get_settings

# DependÃªncia opcional para DEV
from fastapi import Request

def get_current_user_optional(
    request: Request,
    db: Session = Depends(get_db),
):
    settings = get_settings()
    try:
        return get_current_active_user(db=db)
    except Exception:
        if settings.DEBUG:
            return None
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

router = APIRouter(prefix="/notas", tags=["notas"])

settings = get_settings()

@router.get("/", response_model=PaginatedResponse[NotaResponse])
async def get_notas(
    page: int = Query(1, ge=1, description="NÃºmero da pÃ¡gina"),
    page_size: int = Query(25, ge=1, le=100, description="Tamanho da pÃ¡gina"),
    status_filter: Optional[StatusNota] = Query(None, description="Filtrar por status"),
    fornecedor_id: Optional[int] = Query(None, description="Filtrar por fornecedor"),
    data_inicio: Optional[date] = Query(None, description="Data de inÃ­cio"),
    data_fim: Optional[date] = Query(None, description="Data de fim"),
    search: Optional[str] = Query(None, description="Busca por nÃºmero, sÃ©rie ou chave"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Listar notas fiscais com paginaÃ§Ã£o e filtros"""
    
    # Construir query base
    query = db.query(Nota)
    
    # Aplicar filtros
    if status_filter:
        query = query.filter(Nota.status == status_filter)
    
    if fornecedor_id:
        query = query.filter(Nota.fornecedor_id == fornecedor_id)
    
    if data_inicio:
        query = query.filter(Nota.emissao_date >= data_inicio)
    
    if data_fim:
        query = query.filter(Nota.emissao_date <= data_fim)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Nota.numero.ilike(search_term),
                Nota.serie.ilike(search_term),
                Nota.chave_acesso.ilike(search_term)
            )
        )
    
    # Contar total
    total = query.count()
    
    # Aplicar paginaÃ§Ã£o
    offset = (page - 1) * page_size
    notas = query.order_by(Nota.created_at.desc()).offset(offset).limit(page_size).all()
    
    # Buscar fornecedores e itens para cada nota
    nota_responses = []
    for nota in notas:
        # Buscar fornecedor
        fornecedor = db.query(Fornecedor).filter(
            Fornecedor.id_fornecedor == nota.fornecedor_id
        ).first()
        
        fornecedor_dict = None
        if fornecedor:
            fornecedor_dict = {
                "id": fornecedor.id_fornecedor,
                "nome": fornecedor.nome,
            }
        
        # Buscar itens
        itens = db.query(NotaItem).filter(NotaItem.nota_id == nota.id).all()
        
        nota_response = NotaResponse(
            id=nota.id,
            numero=nota.numero,
            serie=nota.serie,
            chave_acesso=nota.chave_acesso,
            fornecedor_id=nota.fornecedor_id,
            emissao_date=nota.emissao_date,
            valor_total=nota.valor_total,
            arquivo_xml_path=nota.arquivo_xml_path,
            arquivo_pdf_path=nota.arquivo_pdf_path,
            file_hash=nota.file_hash,
            status=nota.status,
            is_active=nota.is_active,
            created_at=nota.created_at.isoformat(),
            updated_at=nota.updated_at.isoformat() if nota.updated_at else None,
            fornecedor=fornecedor_dict,
            itens=[NotaItemResponse(
                id=item.id,
                materia_prima_id=item.materia_prima_id,
                nome_no_documento=item.nome_no_documento,
                unidade_codigo=item.unidade_codigo,
                quantidade=item.quantidade,
                valor_unitario=item.valor_unitario,
                valor_total=item.valor_total
            ) for item in itens]
        )
        nota_responses.append(nota_response)
    
    return PaginatedResponse(
        items=nota_responses,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.get("/{nota_id}", response_model=NotaResponse)
async def get_nota(
    nota_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obter uma nota fiscal especÃ­fica"""
    
    nota = db.query(Nota).filter(Nota.id == nota_id).first()
    if not nota:
        raise HTTPException(status_code=404, detail="Nota fiscal nÃ£o encontrada")
    
    # Buscar fornecedor
    fornecedor = db.query(Fornecedor).filter(
        Fornecedor.id_fornecedor == nota.fornecedor_id
    ).first()
    
    fornecedor_dict = None
    if fornecedor:
        fornecedor_dict = {
            "id": fornecedor.id_fornecedor,
            "nome": fornecedor.nome,
        }
    
    # Buscar itens
    itens = db.query(NotaItem).filter(NotaItem.nota_id == nota.id).all()
    
    return NotaResponse(
        id=nota.id,
        numero=nota.numero,
        serie=nota.serie,
        chave_acesso=nota.chave_acesso,
        fornecedor_id=nota.fornecedor_id,
        emissao_date=nota.emissao_date,
        valor_total=nota.valor_total,
        arquivo_xml_path=nota.arquivo_xml_path,
        arquivo_pdf_path=nota.arquivo_pdf_path,
        file_hash=nota.file_hash,
        status=nota.status,
        is_active=nota.is_active,
        created_at=nota.created_at.isoformat(),
        updated_at=nota.updated_at.isoformat() if nota.updated_at else None,
        fornecedor=fornecedor_dict,
        itens=[NotaItemResponse(
            id=item.id,
            materia_prima_id=item.materia_prima_id,
            nome_no_documento=item.nome_no_documento,
            unidade_codigo=item.unidade_codigo,
            quantidade=item.quantidade,
            valor_unitario=item.valor_unitario,
            valor_total=item.valor_total
        ) for item in itens]
    )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_nota(
    nota_data: NotaCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    try:
        print(f"DEBUG: Criando nota - Numero: {nota_data.numero}, Itens: {len(nota_data.itens)}")
        
        # Criar a nota
        nota = Nota(
            numero=nota_data.numero,
            serie=nota_data.serie,
            chave_acesso=nota_data.chave_acesso,
            fornecedor_id=nota_data.fornecedor_id,
            emissao_date=nota_data.emissao_date,
            valor_total=nota_data.valor_total,
            status=StatusNota.rascunho
        )
        
        db.add(nota)
        db.flush()  # Para obter o ID
        
        print(f"DEBUG: Nota criada com ID: {nota.id}")
        
        # Criar os itens da nota
        for i, item_data in enumerate(nota_data.itens):
            print(f"DEBUG: Processando item {i+1}: {item_data.nome_no_documento}")
            
            # Buscar matÃ©ria-prima existente pelo nome
            nome_limpo = item_data.nome_no_documento.replace('-', '').replace('(', '').replace(')', '').strip()
            materia_prima = db.query(MateriaPrima).filter(
                MateriaPrima.nome.ilike(f"%{nome_limpo}%")
            ).first()
            
            materia_prima_id = None
            if materia_prima:
                materia_prima_id = materia_prima.id
                print(f"DEBUG: MatÃ©ria-prima encontrada: {materia_prima.nome}")
            else:
                print(f"DEBUG: MatÃ©ria-prima nÃ£o encontrada para: {item_data.nome_no_documento}")
            
            # Verificar se a unidade existe, se nÃ£o, criar automaticamente
            unidade = db.query(Unidade).filter(Unidade.codigo == item_data.unidade_codigo).first()
            if not unidade:
                # CORREÃ‡ÃƒO: Usar menor_unidade_id ao invÃ©s de menor_unidade_codigo
                unidade = Unidade(
                    codigo=item_data.unidade_codigo,
                    descricao=item_data.unidade_codigo.upper(),
                    fator_para_menor=1.0,
                    menor_unidade_id=None,  # CORRIGIDO: Era menor_unidade_codigo
                    is_base=True
                )
                db.add(unidade)
                db.flush()  # Para obter o ID
                print(f"DEBUG: Unidade '{item_data.unidade_codigo}' criada automaticamente")
            
            # Criar item da nota
            item = NotaItem(
                nota_id=nota.id,
                materia_prima_id=materia_prima_id,
                nome_no_documento=item_data.nome_no_documento,
                unidade_codigo=item_data.unidade_codigo,
                quantidade=item_data.quantidade,
                valor_unitario=item_data.valor_unitario,
                valor_total=item_data.valor_total
            )
            db.add(item)
            print(f"DEBUG: Item criado: {item_data.nome_no_documento}")
        
        db.commit()
        db.refresh(nota)
        
        print(f"DEBUG: Nota salva com sucesso!")
        
        # Buscar fornecedor para resposta
        fornecedor = db.query(Fornecedor).filter(
            Fornecedor.id_fornecedor == nota.fornecedor_id
        ).first()
        
        fornecedor_dict = None
        if fornecedor:
            fornecedor_dict = {
                "id": fornecedor.id_fornecedor,
                "nome": fornecedor.nome,
            }
        
        # Buscar itens para resposta
        itens = db.query(NotaItem).filter(NotaItem.nota_id == nota.id).all()
        
        # Retornar no formato esperado pelo frontend
        nota_response = NotaResponse(
            id=nota.id,
            numero=nota.numero,
            serie=nota.serie,
            chave_acesso=nota.chave_acesso,
            fornecedor_id=nota.fornecedor_id,
            emissao_date=nota.emissao_date,
            valor_total=nota.valor_total,
            arquivo_xml_path=nota.arquivo_xml_path,
            arquivo_pdf_path=nota.arquivo_pdf_path,
            file_hash=nota.file_hash,
            status=nota.status,
            is_active=nota.is_active,
            created_at=nota.created_at.isoformat(),
            updated_at=nota.updated_at.isoformat() if nota.updated_at else None,
            fornecedor=fornecedor_dict,
            itens=[NotaItemResponse(
                id=item.id,
                materia_prima_id=item.materia_prima_id,
                nome_no_documento=item.nome_no_documento,
                unidade_codigo=item.unidade_codigo,
                quantidade=item.quantidade,
                valor_unitario=item.valor_unitario,
                valor_total=item.valor_total
            ) for item in itens]
        )
        
        return {
            "success": True,
            "message": "Nota fiscal cadastrada com sucesso!",
            "data": nota_response
        }
        
    except Exception as e:
        print(f"ERROR: Erro ao criar nota: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )


@router.put("/{nota_id}", response_model=NotaResponse)
async def update_nota(
    nota_id: int,
    nota_data: NotaUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_editor)
):
    """Atualizar uma nota fiscal"""
    
    nota = db.query(Nota).filter(Nota.id == nota_id).first()
    if not nota:
        raise HTTPException(status_code=404, detail="Nota fiscal nÃ£o encontrada")
    
    # Atualizar campos
    for field, value in nota_data.dict(exclude_unset=True).items():
        if hasattr(nota, field):
            setattr(nota, field, value)
    
    db.commit()
    db.refresh(nota)
    
    return nota


@router.delete("/{nota_id}")
async def delete_nota(
    nota_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_editor)
):
    """Deletar uma nota fiscal"""
    
    nota = db.query(Nota).filter(Nota.id == nota_id).first()
    if not nota:
        raise HTTPException(status_code=404, detail="Nota fiscal nÃ£o encontrada")
    
    # Deletar itens primeiro
    db.query(NotaItem).filter(NotaItem.nota_id == nota_id).delete()
    
    # Deletar nota
    db.delete(nota)
    db.commit()
    
    return {"message": "Nota fiscal deletada com sucesso"}


@router.post("/import")
async def import_notas(
    files: List[UploadFile] = File(...),
    commit: bool = Form(False, description="Confirmar importaÃ§Ã£o"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Importar notas fiscais de arquivos XML"""
    
    resultados = []
    
    for file in files:
        try:
            content = await file.read()
            
            # Processar XML (simplificado)
            root = etree.fromstring(content)
            
            # Extrair dados bÃ¡sicos
            numero = root.find(".//nNF").text if root.find(".//nNF") is not None else ""
            serie = root.find(".//serie").text if root.find(".//serie") is not None else ""
            chave = root.find(".//chNFe").text if root.find(".//chNFe") is not None else ""
            
            resultados.append({
                "arquivo": file.filename,
                "numero": numero,
                "serie": serie,
                "chave": chave,
                "status": "processado"
            })
            
        except Exception as e:
            resultados.append({
                "arquivo": file.filename,
                "erro": str(e),
                "status": "erro"
            })
    
    return {
        "success": True,
        "message": f"{len(resultados)} arquivos processados",
        "resultados": resultados
    }
