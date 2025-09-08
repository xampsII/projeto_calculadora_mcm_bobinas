# backend/app/models/enums.py
from enum import Enum

class UserRole(str, Enum):
    admin = "admin"
    editor = "editor"
    viewer = "viewer"

class AuditAction(str, Enum):
    create = "create"
    update = "update"
    delete = "delete"

class OrigemPreco(str, Enum):
    manual = "manual"
    nota_xml = "nota_xml"
    nota_pdf = "nota_pdf"
    api = "api"

class StatusNota(str, Enum):
    rascunho = "rascunho"
    processando = "processando"
    processada = "processada"
    falha = "falha" 