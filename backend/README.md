# Sistema NFE - Backend

Sistema completo de Nota Fiscal Eletrônica (NFE) com gestão de fornecedores, matérias-primas, produtos e histórico de preços.

## Pré-requisitos

- Python 3.11+
- PostgreSQL 14+
- Redis 6+
- Tesseract OCR (para processamento de PDFs)

## Instalação Local

### 1. Configuração do Ambiente

```bash
# Clone o repositório
git clone <url-do-repositorio>
cd project

# Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Instale as dependências
make install
```

### 2. Configuração do Banco de Dados

```bash
# Crie o banco PostgreSQL
createdb nfe_system

# Execute as migrações
make migrate

# Popule com dados iniciais
make seed
```

### 3. Configuração do Redis

```bash
# Inicie o Redis (Linux/Mac)
redis-server

# Windows: Baixe e execute o Redis
# https://github.com/microsoftarchive/redis/releases
```

### 4. Configuração das Variáveis de Ambiente

Copie o arquivo `.env.example` para `.env` e configure:

```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

## Execução

### Desenvolvimento

```bash
# Terminal 1: API
make run

# Terminal 2: Worker Celery
make worker

# Terminal 3: Scheduler Celery
make beat
```

### Comandos Úteis

```bash
make help          # Lista todos os comandos
make test          # Executa os testes
make clean         # Limpa arquivos temporários
make health        # Verifica status dos serviços
make setup         # Setup completo do projeto
```

## Estrutura do Projeto

```
backend/
├── app/
│   ├── api/           # Rotas da API
│   ├── auth/          # Autenticação e autorização
│   ├── models/        # Modelos SQLAlchemy
│   ├── schemas/       # Schemas Pydantic
│   ├── tasks/         # Tarefas Celery
│   └── utils/         # Utilitários
├── alembic/           # Migrações do banco
├── tests/             # Testes
└── requirements.txt   # Dependências Python
```

## Funcionalidades

- **Gestão de Usuários**: RBAC com roles admin, editor, viewer
- **Fornecedores**: CRUD completo com validação de CNPJ
- **Matérias-Primas**: Catálogo com histórico de preços
- **Notas Fiscais**: Upload de XML/PDF, processamento automático
- **Produtos**: Estrutura de BOM com cálculo automático de custos
- **Históricos**: Rastreamento de variações de preços
- **Auditoria**: Log completo de todas as alterações
- **Integrações**: Processamento de emails IMAP

## API Endpoints

- `POST /auth/login` - Login de usuário
- `GET /users/` - Lista usuários (admin)
- `GET /fornecedores/` - Lista fornecedores
- `POST /materias-primas/` - Cria matéria-prima
- `GET /notas/` - Lista notas fiscais
- `POST /produtos/` - Cria produto
- `GET /historicos/` - Histórico de preços

## Desenvolvimento

### Adicionando Novas Funcionalidades

1. Crie o modelo em `app/models/`
2. Crie os schemas em `app/schemas/`
3. Crie as rotas em `app/api/`
4. Adicione testes em `tests/`
5. Execute `make test` para validar

### Migrações

```bash
# Criar nova migração
cd backend && alembic revision --autogenerate -m "descrição"

# Aplicar migrações
make migrate
```

## Troubleshooting

### Problemas Comuns

1. **Erro de conexão com PostgreSQL**: Verifique se o serviço está rodando
2. **Erro de conexão com Redis**: Verifique se o Redis está ativo
3. **Erro de permissão**: Verifique as configurações do banco

### Logs

```bash
make logs  # Mostra logs da aplicação
```

## Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request 