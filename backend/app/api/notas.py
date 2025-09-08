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

# Dependência opcional para DEV
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
logger = logging.getLogger(__name__)


@router.get("/", response_model=PaginatedResponse[NotaResponse])
async def list_notas(
    query: Optional[str] = Query(None, description="Buscar por número, série ou chave de acesso"),
    periodo_ini: Optional[date] = Query(None, description="Data de emissão inicial"),
    periodo_fim: Optional[date] = Query(None, description="Data de emissão final"),
    fornecedor: Optional[str] = Query(None, description="Filtrar por fornecedor"),
    materia_prima: Optional[str] = Query(None, description="Filtrar por matéria-prima"),
    page: int = Query(1, ge=1, description="Número da página"),
    page_size: int = Query(10, ge=1, le=100, description="Tamanho da página"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Lista notas fiscais com paginação e filtros"""
    if not current_user and not get_settings().DEBUG:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    # Query base - apenas notas ativas
    query_obj = db.query(Nota).filter(Nota.is_active == True)
    
    if query:
        query_obj = query_obj.filter(
            or_(
                Nota.numero.ilike(f"%{query}%"),
                Nota.serie.ilike(f"%{query}%"),
                Nota.chave_acesso.ilike(f"%{query}%") if Nota.chave_acesso else False
            )
        )
    
    if periodo_ini:
        query_obj = query_obj.filter(Nota.emissao_date >= periodo_ini)
    
    if periodo_fim:
        query_obj = query_obj.filter(Nota.emissao_date <= periodo_fim)
    
    if fornecedor:
        query_obj = query_obj.join(Fornecedor).filter(
            or_(
                Fornecedor.nome.ilike(f"%{fornecedor}%"),
                Fornecedor.cnpj.ilike(f"%{fornecedor}%")
            )
        )
    
    if materia_prima:
        query_obj = query_obj.join(NotaItem).join(MateriaPrima).filter(
            MateriaPrima.nome.ilike(f"%{materia_prima}%")
        )
    
    total = query_obj.count()
    offset = (page - 1) * page_size
    
    notas = query_obj.offset(offset).limit(page_size).all()
    
    # Buscar fornecedor e itens para cada nota
    items = []
    for nota in notas:
        fornecedor = db.query(Fornecedor).filter(Fornecedor.id == nota.fornecedor_id).first()
        itens = db.query(NotaItem).filter(NotaItem.nota_id == nota.id).all()
        
        # Criar dicionário do fornecedor
        fornecedor_dict = None
        if fornecedor:
            fornecedor_dict = {
                "id": fornecedor.id,
                "nome": fornecedor.nome,
                "cnpj": fornecedor.cnpj
            }
        
        items.append(NotaResponse(
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
        ))
    
    # Calcular total de páginas
    total_pages = (total + page_size - 1) // page_size
    
    return PaginatedResponse(
        items=items,
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages
    )


@router.get("/{nota_id}", response_model=NotaResponse)
async def get_nota(
    nota_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtém detalhes de uma nota fiscal específica"""
    nota = db.query(Nota).filter(Nota.id == nota_id).first()
    
    if not nota:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nota fiscal não encontrada"
        )
    
    fornecedor = db.query(Fornecedor).filter(Fornecedor.id == nota.fornecedor_id).first()
    itens = db.query(NotaItem).filter(NotaItem.nota_id == nota.id).all()
    
    # Criar dicionário do fornecedor
    fornecedor_dict = None
    if fornecedor:
        fornecedor_dict = {
            "id": fornecedor.id,
            "nome": fornecedor.nome,
            "cnpj": fornecedor.cnpj
        }
    
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


@router.post("/", response_model=NotaResponse, status_code=status.HTTP_201_CREATED)
async def create_nota(
    nota_data: NotaCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    if not current_user and not get_settings().DEBUG:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    # Verificar se já existe nota com a mesma chave de acesso
    if nota_data.chave_acesso:
        existing_nota = db.query(Nota).filter(
            Nota.chave_acesso == nota_data.chave_acesso
        ).first()
        
        if existing_nota:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Já existe uma nota com esta chave de acesso"
            )
    
    # Verificar se o fornecedor existe
    fornecedor = db.query(Fornecedor).filter(
        and_(
            Fornecedor.id == nota_data.fornecedor_id,
            Fornecedor.is_active == True
        )
    ).first()
    
    if not fornecedor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Fornecedor não encontrado"
        )
    
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
    db.commit()
    db.refresh(nota)
    
    # Criar os itens da nota
    for item_data in nota_data.itens:
        # Verificar se a matéria-prima existe
        materia_prima = None
        if item_data.materia_prima_id:
            materia_prima = db.query(MateriaPrima).filter(
                and_(
                    MateriaPrima.id == item_data.materia_prima_id,
                    MateriaPrima.is_active == True
                )
            ).first()
            
            if not materia_prima:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Matéria-prima com ID {item_data.materia_prima_id} não encontrada"
                )
        else:
            # Criar matéria-prima automaticamente se não existir
            materia_prima = db.query(MateriaPrima).filter(
                and_(
                    MateriaPrima.nome == item_data.nome_no_documento,
                    MateriaPrima.is_active == True
                )
            ).first()
            
            if not materia_prima:
                # Verificar se a unidade existe
                unidade = db.query(Unidade).filter(
                    Unidade.codigo == item_data.unidade_codigo
                ).first()
                
                if not unidade:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Unidade {item_data.unidade_codigo} não encontrada"
                    )
                
                materia_prima = MateriaPrima(
                    nome=item_data.nome_no_documento,
                    unidade_codigo=item_data.unidade_codigo
                )
                
                db.add(materia_prima)
                db.commit()
                db.refresh(materia_prima)
        
        # Criar o item da nota
        item = NotaItem(
            nota_id=nota.id,
            materia_prima_id=materia_prima.id,
            nome_no_documento=item_data.nome_no_documento,
            unidade_codigo=item_data.unidade_codigo,
            quantidade=item_data.quantidade,
            valor_unitario=item_data.valor_unitario,
            valor_total=item_data.valor_total
        )
        
        db.add(item)
        
        # Criar/atualizar preço da matéria-prima
        preco_existente = db.query(MateriaPrimaPreco).filter(
            and_(
                MateriaPrimaPreco.materia_prima_id == materia_prima.id,
                MateriaPrimaPreco.vigente_ate.is_(None)
            )
        ).first()
        
        if preco_existente:
            # Fechar preço anterior
            preco_existente.vigente_ate = nota.emissao_date
            db.add(preco_existente)
        
        novo_preco = MateriaPrimaPreco(
            materia_prima_id=materia_prima.id,
            valor_unitario=item_data.valor_unitario,
            vigente_desde=nota.emissao_date,
            fornecedor_id=nota.fornecedor_id,
            nota_id=nota.id
        )
        
        db.add(novo_preco)
    
    db.commit()
    
    # Log de auditoria
    await log_audit(
        db=db,
        user_id=current_user.id,
        entity="nota",
        entity_id=nota.id,
        action="create",
        changes={
            "numero": nota.numero,
            "serie": nota.serie,
            "fornecedor_id": nota.fornecedor_id,
            "valor_total": float(nota.valor_total)
        }
    )
    
    # Buscar dados atualizados para resposta
    db.refresh(nota)
    itens = db.query(NotaItem).filter(NotaItem.nota_id == nota.id).all()
    
    # Criar dicionário do fornecedor
    fornecedor_dict = None
    if fornecedor:
        fornecedor_dict = {
            "id": fornecedor.id,
            "nome": fornecedor.nome,
            "cnpj": fornecedor.cnpj
        }
    
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


@router.put("/{nota_id}", response_model=NotaResponse)
async def update_nota(
    nota_id: int,
    nota_data: NotaUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_editor)
):
    """Atualiza uma nota fiscal existente"""
    nota = db.query(Nota).filter(Nota.id == nota_id).first()
    
    if not nota:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nota fiscal não encontrada"
        )
    
    # Verificar se a chave de acesso já existe em outra nota
    if nota_data.chave_acesso and nota_data.chave_acesso != nota.chave_acesso:
        existing_nota = db.query(Nota).filter(
            and_(
                Nota.chave_acesso == nota_data.chave_acesso,
                Nota.id != nota_id
            )
        ).first()
        
        if existing_nota:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Já existe uma nota com esta chave de acesso"
            )
    
    # Capturar mudanças para auditoria
    changes = {}
    
    if nota_data.numero and nota_data.numero != nota.numero:
        changes["numero"] = {"before": nota.numero, "after": nota_data.numero}
        nota.numero = nota_data.numero
    
    if nota_data.serie and nota_data.serie != nota.serie:
        changes["serie"] = {"before": nota.serie, "after": nota_data.serie}
        nota.serie = nota_data.serie
    
    if nota_data.chave_acesso != nota.chave_acesso:
        changes["chave_acesso"] = {"before": nota.chave_acesso, "after": nota_data.chave_acesso}
        nota.chave_acesso = nota_data.chave_acesso
    
    if nota_data.emissao_date and nota_data.emissao_date != nota.emissao_date:
        changes["emissao_date"] = {"before": nota.emissao_date, "after": nota_data.emissao_date}
        nota.emissao_date = nota_data.emissao_date
    
    if nota_data.valor_total and nota_data.valor_total != nota.valor_total:
        changes["valor_total"] = {"before": float(nota.valor_total), "after": float(nota_data.valor_total)}
        nota.valor_total = nota_data.valor_total
    
    if changes:
        db.commit()
        db.refresh(nota)
        
        # Log de auditoria
        await log_audit(
            db=db,
            user_id=current_user.id,
            entity="nota",
            entity_id=nota.id,
            action="update",
            changes=changes
        )
    
    # Buscar dados atualizados para resposta
    fornecedor = db.query(Fornecedor).filter(Fornecedor.id == nota.fornecedor_id).first()
    itens = db.query(NotaItem).filter(NotaItem.nota_id == nota.id).all()
    
    # Criar dicionário do fornecedor
    fornecedor_dict = None
    if fornecedor:
        fornecedor_dict = {
            "id": fornecedor.id,
            "nome": fornecedor.nome,
            "cnpj": fornecedor.cnpj
        }
    
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


@router.delete("/{nota_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_nota(
    nota_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_editor)
):
    """Soft delete de uma nota fiscal"""
    nota = db.query(Nota).filter(Nota.id == nota_id).first()
    
    if not nota:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nota fiscal não encontrada"
        )
    
    # Verificar se há preços de matéria-prima vinculados
    precos_vinculados = db.query(MateriaPrimaPreco).filter(
        MateriaPrimaPreco.nota_id == nota_id
    ).first()
    
    if precos_vinculados:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Não é possível excluir nota que possui preços de matéria-prima vinculados"
        )
    
    # Soft delete
    nota.is_active = False
    db.commit()
    
    # Log de auditoria
    await log_audit(
        db=db,
        user_id=current_user.id,
        entity="nota",
        entity_id=nota.id,
        action="delete",
        changes={"is_active": {"before": True, "after": False}}
    )


@router.post("/import")
async def import_notas(
    files: List[UploadFile] = File(...),
    commit: bool = Form(False, description="Confirmar importação"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Importa notas fiscais a partir de arquivos XML/PDF"""
    if not current_user and not get_settings().DEBUG:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nenhum arquivo fornecido"
        )
    
    resultados = []
    
    for file in files:
        if file.filename:
            # Verificar extensão do arquivo
            if not file.filename.lower().endswith(('.xml', '.pdf')):
                resultados.append({
                    "arquivo": file.filename,
                    "status": "erro",
                    "mensagem": "Formato de arquivo não suportado. Use XML ou PDF."
                })
                continue
            
            # Calcular hash do arquivo
            content = await file.read()
            file_hash = hashlib.md5(content).hexdigest()
            
            # Verificar se o arquivo já foi processado
            nota_existente = db.query(Nota).filter(Nota.file_hash == file_hash).first()
            
            if nota_existente:
                resultados.append({
                    "arquivo": file.filename,
                    "status": "duplicado",
                    "mensagem": f"Arquivo já foi processado (Nota ID: {nota_existente.id})"
                })
                continue
            
            if commit:
                # Salvar arquivo
                upload_dir = "uploads"
                os.makedirs(upload_dir, exist_ok=True)
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_filename = f"{timestamp}_{file.filename}"
                file_path = os.path.join(upload_dir, safe_filename)
                
                with open(file_path, "wb") as f:
                    f.write(content)
                
                # Criar ou obter fornecedor padrão
                fornecedor_padrao = db.query(Fornecedor).filter(Fornecedor.cnpj == "00000000000000").first()
                if not fornecedor_padrao:
                    fornecedor_padrao = Fornecedor(
                        cnpj="00000000000000",
                        nome="Fornecedor Padrão",
                        endereco="Endereço não disponível"
                    )
                    db.add(fornecedor_padrao)
                    db.commit()
                    db.refresh(fornecedor_padrao)
                
                # Criar nota com status "processando"
                nota = Nota(
                    numero=f"IMP_{timestamp}",
                    serie="IMP",
                    file_hash=file_hash,
                    status=StatusNota.processando,
                    emissao_date=datetime.now().date(),
                    valor_total=0.0,
                    fornecedor_id=fornecedor_padrao.id
                )
                
                if file.filename.lower().endswith('.xml'):
                    nota.arquivo_xml_path = file_path
                else:
                    nota.arquivo_pdf_path = file_path
                
                db.add(nota)
                db.commit()
                db.refresh(nota)
                
                # Processar arquivo XML diretamente
                try:
                    if file.filename.lower().endswith('.xml'):
                        # Ler e parsear XML
                        with open(file_path, 'rb') as f:
                            xml_content = f.read()
                        
                        root = etree.fromstring(xml_content)
                        
                        # Definir namespaces
                        namespaces = {
                            'nfe': 'http://www.portalfiscal.inf.br/nfe'
                        }
                        
                        # Extrair dados básicos
                        chave_acesso = root.find('.//nfe:chNFe', namespaces)
                        if chave_acesso is not None and chave_acesso.text:
                            nota.chave_acesso = chave_acesso.text
                        
                        numero = root.find('.//nfe:nNF', namespaces)
                        if numero is not None and numero.text:
                            nota.numero = numero.text
                        
                        serie = root.find('.//nfe:serie', namespaces)
                        if serie is not None and serie.text:
                            nota.serie = serie.text
                        
                        # Data de emissão
                        dh_emi = root.find('.//nfe:dhEmi', namespaces)
                        if dh_emi is not None and dh_emi.text:
                            try:
                                data_str = dh_emi.text.split('T')[0]
                                nota.emissao_date = datetime.strptime(data_str, '%Y-%m-%d').date()
                            except:
                                pass
                        
                        # Fornecedor
                        emit_cnpj = root.find('.//nfe:emit/nfe:CNPJ', namespaces)
                        emit_nome = root.find('.//nfe:emit/nfe:xNome', namespaces)
                        
                        if emit_cnpj is not None and emit_cnpj.text:
                            fornecedor = db.query(Fornecedor).filter(
                                Fornecedor.cnpj == emit_cnpj.text
                            ).first()
                            
                            if not fornecedor:
                                fornecedor = Fornecedor(
                                    cnpj=emit_cnpj.text,
                                    nome=emit_nome.text if emit_nome is not None else "Fornecedor não identificado",
                                    endereco="Endereço não disponível"
                                )
                                db.add(fornecedor)
                                db.commit()
                                db.refresh(fornecedor)
                            
                            nota.fornecedor_id = fornecedor.id
                        
                        # Valor total
                        v_nf = root.find('.//nfe:vNF', namespaces)
                        if v_nf is not None and v_nf.text:
                            try:
                                nota.valor_total = float(v_nf.text)
                            except:
                                pass
                        
                        # Extrair itens dos produtos
                        itens = []
                        for det in root.findall('.//nfe:det', namespaces):
                            item = {}
                            
                            # Código do produto
                            c_prod = det.find('.//nfe:cProd', namespaces)
                            if c_prod is not None and c_prod.text:
                                item['codigo'] = c_prod.text
                            
                            # Descrição do produto
                            x_prod = det.find('.//nfe:xProd', namespaces)
                            if x_prod is not None and x_prod.text:
                                item['descricao'] = x_prod.text
                            
                            # Quantidade
                            q_com = det.find('.//nfe:qCom', namespaces)
                            if q_com is not None and q_com.text:
                                try:
                                    item['quantidade'] = float(q_com.text)
                                except:
                                    item['quantidade'] = 0.0
                            
                            # Valor unitário
                            v_un_com = det.find('.//nfe:vUnCom', namespaces)
                            if v_un_com is not None and v_un_com.text:
                                try:
                                    item['valor_unitario'] = float(v_un_com.text)
                                except:
                                    item['valor_unitario'] = 0.0
                            
                            # Valor total do item
                            v_prod = det.find('.//nfe:vProd', namespaces)
                            if v_prod is not None and v_prod.text:
                                try:
                                    item['valor_total'] = float(v_prod.text)
                                except:
                                    item['valor_total'] = 0.0
                            
                            # Unidade
                            u_com = det.find('.//nfe:uCom', namespaces)
                            if u_com is not None and u_com.text:
                                item['unidade'] = u_com.text
                            
                            if item:
                                itens.append(item)
                        
                        # Marcar como processada
                        nota.status = StatusNota.processada
                        db.commit()
                        
                        logger.info(f"XML processado com sucesso: {nota.numero}")
                    else:
                        # PDF - marcar como falha por enquanto
                        nota.status = StatusNota.falha
                        db.commit()
                        logger.info("PDF marcado como falha (parsing não implementado)")
                        
                except Exception as e:
                    logger.error(f"Erro ao processar arquivo: {e}")
                    nota.status = StatusNota.falha
                    db.commit()
                
                resultados.append({
                    "arquivo": file.filename,
                    "status": "sucesso",
                    "mensagem": f"Arquivo importado com sucesso (Nota ID: {nota.id})",
                    "dados": {
                        "numero": nota.numero,
                        "serie": nota.serie,
                        "chave_acesso": nota.chave_acesso,
                        "emissao_date": nota.emissao_date.isoformat() if nota.emissao_date else None,
                        "valor_total": nota.valor_total,
                        "fornecedor": {
                            "nome": fornecedor.nome if nota.fornecedor_id else None,
                            "cnpj": fornecedor.cnpj if nota.fornecedor_id else None,
                            "endereco": fornecedor.endereco if nota.fornecedor_id else None
                        } if nota.fornecedor_id else None,
                        "itens": itens
                    }
                })
            else:
                # Preview mode
                resultados.append({
                    "arquivo": file.filename,
                    "status": "preview",
                    "mensagem": "Arquivo seria importado (use commit=true para confirmar)",
                    "file_hash": file_hash
                })
    
    return {
        "success": True,
        "message": f"Processados {len(resultados)} arquivos",
        "resultados": resultados,
        "commit": commit,
        "total_arquivos": len(files)
    }


@router.post("/fetch-by-api-key")
async def fetch_nota_by_api_key(
    api_key: str,
    chave_acesso: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Stub para buscar nota via API externa (implementação futura)"""
    # TODO: Implementar integração com API externa
    return {
        "message": "Funcionalidade em desenvolvimento",
        "api_key": api_key,
        "chave_acesso": chave_acesso
    } 