from typing import Any, Dict, Optional
from sqlalchemy.orm import Session
from app.models.audit import AuditLog, AuditAction
from app.models.user import User
import json


def log_audit(
    db: Session,
    user: User,
    entity: str,
    entity_id: int,
    action: AuditAction,
    changes: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None
) -> None:
    """Registra uma entrada de auditoria"""
    audit_log = AuditLog(
        user_id=user.id,
        entity=entity,
        entity_id=entity_id,
        action=action,
        changes=changes,
        ip_address=ip_address
    )
    db.add(audit_log)
    db.commit()


def create_changes_dict(
    before: Optional[Dict[str, Any]] = None,
    after: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Cria dicionário de mudanças para auditoria"""
    changes = {}
    
    if before:
        changes["before"] = before
    
    if after:
        changes["after"] = after
    
    return changes


def get_entity_changes(
    db_obj: Any,
    update_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Obtém mudanças entre objeto atual e dados de atualização"""
    before = {}
    after = {}
    
    for field, new_value in update_data.items():
        if hasattr(db_obj, field):
            old_value = getattr(db_obj, field)
            if old_value != new_value:
                before[field] = str(old_value) if old_value is not None else None
                after[field] = str(new_value) if new_value is not None else None
    
    return create_changes_dict(before, after) 