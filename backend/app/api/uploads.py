from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
import hashlib
import os
from datetime import datetime
import mimetypes

from app.database import get_db
from app.models.user import User
from app.auth.dependencies import get_current_active_user, require_editor
from app.config import get_settings

router = APIRouter(prefix="/uploads", tags=["uploads"])

settings = get_settings()

# Tipos de arquivo permitidos
ALLOWED_EXTENSIONS = {
    '.xml': 'application/xml',
    '.pdf': 'application/pdf',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.png': 'image/png',
    '.txt': 'text/plain'
}

# Tamanho máximo de arquivo (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024


@router.post("/")
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_editor)
):
    """Faz upload de um arquivo único"""
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nome do arquivo é obrigatório"
        )
    
    # Verificar extensão do arquivo
    file_extension = os.path.splitext(file.filename.lower())[1]
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de arquivo não suportado. Extensões permitidas: {', '.join(ALLOWED_EXTENSIONS.keys())}"
        )
    
    # Ler conteúdo do arquivo
    try:
        content = await file.read()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao ler arquivo: {str(e)}"
        )
    
    # Verificar tamanho do arquivo
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Arquivo muito grande. Tamanho máximo permitido: {MAX_FILE_SIZE / (1024*1024):.1f}MB"
        )
    
    # Calcular hash do arquivo
    file_hash = hashlib.md5(content).hexdigest()
    
    # Criar diretório de uploads se não existir
    upload_dir = settings.UPLOAD_DIR
    os.makedirs(upload_dir, exist_ok=True)
    
    # Gerar nome único para o arquivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{file_hash[:8]}_{file.filename}"
    file_path = os.path.join(upload_dir, safe_filename)
    
    # Verificar se arquivo com mesmo hash já existe
    if os.path.exists(file_path):
        # Arquivo já existe, retornar informações
        file_size = os.path.getsize(file_path)
        file_info = {
            "file_id": file_hash,
            "filename": file.filename,
            "safe_filename": safe_filename,
            "file_path": file_path,
            "file_size": file_size,
            "file_hash": file_hash,
            "mime_type": ALLOWED_EXTENSIONS.get(file_extension, 'application/octet-stream'),
            "uploaded_at": datetime.fromtimestamp(os.path.getctime(file_path)),
            "status": "duplicado"
        }
        
        return {
            "message": "Arquivo com mesmo conteúdo já existe",
            "file_info": file_info
        }
    
    # Salvar arquivo
    try:
        with open(file_path, "wb") as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao salvar arquivo: {str(e)}"
        )
    
    # Obter informações do arquivo salvo
    file_size = os.path.getsize(file_path)
    file_info = {
        "file_id": file_hash,
        "filename": file.filename,
        "safe_filename": safe_filename,
        "file_path": file_path,
        "file_size": file_size,
        "file_hash": file_hash,
        "mime_type": ALLOWED_EXTENSIONS.get(file_extension, 'application/octet-stream'),
        "uploaded_at": datetime.now(),
        "status": "sucesso"
    }
    
    return {
        "message": "Arquivo enviado com sucesso",
        "file_info": file_info
    }


@router.post("/multiple")
async def upload_multiple_files(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_editor)
):
    """Faz upload de múltiplos arquivos"""
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nenhum arquivo fornecido"
        )
    
    if len(files) > 10:  # Limite de 10 arquivos por vez
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Máximo de 10 arquivos por upload"
        )
    
    resultados = []
    
    for file in files:
        try:
            if not file.filename:
                resultados.append({
                    "filename": "sem_nome",
                    "status": "erro",
                    "mensagem": "Nome do arquivo é obrigatório"
                })
                continue
            
            # Verificar extensão do arquivo
            file_extension = os.path.splitext(file.filename.lower())[1]
            if file_extension not in ALLOWED_EXTENSIONS:
                resultados.append({
                    "filename": file.filename,
                    "status": "erro",
                    "mensagem": f"Tipo de arquivo não suportado: {file_extension}"
                })
                continue
            
            # Ler conteúdo do arquivo
            content = await file.read()
            
            # Verificar tamanho do arquivo
            if len(content) > MAX_FILE_SIZE:
                resultados.append({
                    "filename": file.filename,
                    "status": "erro",
                    "mensagem": f"Arquivo muito grande: {len(content) / (1024*1024):.1f}MB"
                })
                continue
            
            # Calcular hash do arquivo
            file_hash = hashlib.md5(content).hexdigest()
            
            # Criar diretório de uploads se não existir
            upload_dir = settings.UPLOAD_DIR
            os.makedirs(upload_dir, exist_ok=True)
            
            # Gerar nome único para o arquivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_filename = f"{timestamp}_{file_hash[:8]}_{file.filename}"
            file_path = os.path.join(upload_dir, safe_filename)
            
            # Verificar se arquivo com mesmo hash já existe
            if os.path.exists(file_path):
                resultados.append({
                    "filename": file.filename,
                    "status": "duplicado",
                    "mensagem": "Arquivo com mesmo conteúdo já existe",
                    "file_hash": file_hash,
                    "file_path": file_path
                })
                continue
            
            # Salvar arquivo
            with open(file_path, "wb") as f:
                f.write(content)
            
            resultados.append({
                "filename": file.filename,
                "status": "sucesso",
                "mensagem": "Arquivo enviado com sucesso",
                "file_hash": file_hash,
                "file_path": file_path,
                "file_size": len(content)
            })
            
        except Exception as e:
            resultados.append({
                "filename": file.filename if file.filename else "desconhecido",
                "status": "erro",
                "mensagem": f"Erro interno: {str(e)}"
            })
    
    return {
        "resultados": resultados,
        "total_arquivos": len(files),
        "sucessos": len([r for r in resultados if r["status"] == "sucesso"]),
        "erros": len([r for r in resultados if r["status"] == "erro"]),
        "duplicados": len([r for r in resultados if r["status"] == "duplicado"])
    }


@router.get("/info/{file_hash}")
async def get_file_info(
    file_hash: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtém informações de um arquivo pelo hash"""
    upload_dir = settings.UPLOAD_DIR
    
    # Procurar arquivo pelo hash
    file_path = None
    for filename in os.listdir(upload_dir):
        if filename.endswith(f"_{file_hash[:8]}_"):
            file_path = os.path.join(upload_dir, filename)
            break
    
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Arquivo não encontrado"
        )
    
    # Obter informações do arquivo
    file_stat = os.stat(file_path)
    file_extension = os.path.splitext(file_path)[1]
    
    file_info = {
        "file_hash": file_hash,
        "filename": os.path.basename(file_path),
        "file_path": file_path,
        "file_size": file_stat.st_size,
        "mime_type": ALLOWED_EXTENSIONS.get(file_extension, 'application/octet-stream'),
        "uploaded_at": datetime.fromtimestamp(file_stat.st_ctime),
        "last_modified": datetime.fromtimestamp(file_stat.st_mtime),
        "file_permissions": oct(file_stat.st_mode)[-3:]
    }
    
    return file_info


@router.delete("/{file_hash}")
async def delete_file(
    file_hash: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_editor)
):
    """Remove um arquivo pelo hash"""
    upload_dir = settings.UPLOAD_DIR
    
    # Procurar arquivo pelo hash
    file_path = None
    for filename in os.listdir(upload_dir):
        if filename.endswith(f"_{file_hash[:8]}_"):
            file_path = os.path.join(upload_dir, filename)
            break
    
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Arquivo não encontrado"
        )
    
    try:
        os.remove(file_path)
        return {
            "message": "Arquivo removido com sucesso",
            "file_hash": file_hash,
            "file_path": file_path
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao remover arquivo: {str(e)}"
        )


@router.get("/stats")
async def get_upload_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtém estatísticas dos uploads"""
    upload_dir = settings.UPLOAD_DIR
    
    if not os.path.exists(upload_dir):
        return {
            "total_files": 0,
            "total_size": 0,
            "files_by_type": {},
            "recent_uploads": []
        }
    
    total_files = 0
    total_size = 0
    files_by_type = {}
    recent_uploads = []
    
    for filename in os.listdir(upload_dir):
        file_path = os.path.join(upload_dir, filename)
        
        if os.path.isfile(file_path):
            total_files += 1
            file_size = os.path.getsize(file_path)
            total_size += file_size
            
            # Contar por tipo
            file_extension = os.path.splitext(filename.lower())[1]
            if file_extension in files_by_type:
                files_by_type[file_extension]["count"] += 1
                files_by_type[file_extension]["size"] += file_size
            else:
                files_by_type[file_extension] = {
                    "count": 1,
                    "size": file_size,
                    "mime_type": ALLOWED_EXTENSIONS.get(file_extension, 'application/octet-stream')
                }
            
            # Informações do arquivo para uploads recentes
            file_stat = os.stat(file_path)
            recent_uploads.append({
                "filename": filename,
                "file_size": file_size,
                "uploaded_at": datetime.fromtimestamp(file_stat.st_ctime)
            })
    
    # Ordenar uploads recentes por data
    recent_uploads.sort(key=lambda x: x["uploaded_at"], reverse=True)
    recent_uploads = recent_uploads[:10]  # Top 10 mais recentes
    
    return {
        "total_files": total_files,
        "total_size": total_size,
        "total_size_mb": total_size / (1024 * 1024),
        "files_by_type": files_by_type,
        "recent_uploads": recent_uploads
    } 