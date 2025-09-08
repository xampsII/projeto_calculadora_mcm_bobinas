from celery import Celery
from app.config import get_settings

settings = get_settings()

# Configuração do Celery
celery_app = Celery(
    "nfe_system",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.tasks.email_tasks",
        "app.tasks.parsing_tasks",
        "app.tasks.price_tasks"
    ]
)

# Configurações do Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Sao_Paulo",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutos
    task_soft_time_limit=25 * 60,  # 25 minutos
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    worker_max_memory_per_child=200000,  # 200MB
    broker_connection_retry_on_startup=True,
    result_expires=3600,  # 1 hora
    task_always_eager=False,  # False para produção, True para testes
)

# Configurações específicas para tarefas
celery_app.conf.task_routes = {
    "app.tasks.email_tasks.*": {"queue": "ingestao"},
    "app.tasks.parsing_tasks.*": {"queue": "ingestao"},
    "app.tasks.price_tasks.*": {"queue": "calculos"},
}

# Configurações de beat (agendador)
celery_app.conf.beat_schedule = {
    "processar-emails": {
        "task": "app.tasks.email_tasks.processar_emails_periodico",
        "schedule": 300.0,  # A cada 5 minutos
    },
    "recalcular-custos": {
        "task": "app.tasks.price_tasks.recalcular_custos_periodico",
        "schedule": 3600.0,  # A cada hora
    },
    "limpar-logs-antigos": {
        "task": "app.tasks.maintenance_tasks.limpar_logs_antigos",
        "schedule": 86400.0,  # A cada dia
    },
}

if __name__ == "__main__":
    celery_app.start() 