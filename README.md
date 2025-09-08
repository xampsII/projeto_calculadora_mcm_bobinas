# Sistema NFE - Sistema de Nota Fiscal Eletrônica

Sistema completo para gestão de Notas Fiscais Eletrônicas (NFE) com controle de fornecedores, matérias-primas, produtos e histórico de preços.

## 🚀 Funcionalidades

- **Gestão de Usuários**: Sistema RBAC com roles admin, editor e viewer
- **Fornecedores**: CRUD completo com validação de CNPJ
- **Matérias-Primas**: Catálogo com histórico de preços e variações
- **Notas Fiscais**: Upload de XML/PDF, processamento automático e deduplicação
- **Produtos**: Estrutura de BOM (Bill of Materials) com cálculo automático de custos
- **Históricos**: Rastreamento completo de variações de preços
- **Auditoria**: Log detalhado de todas as alterações com diffs
- **Integrações**: Processamento automático de emails IMAP
- **Conversão de Unidades**: Sistema inteligente de conversão (ex: Rolo → m, Jogo → un)

## 🏗️ Arquitetura

- **Backend**: FastAPI com SQLAlchemy 2 ORM
- **Banco**: PostgreSQL com Alembic para migrações
- **Cache/Fila**: Redis + Celery para tarefas assíncronas
- **Autenticação**: JWT com refresh tokens
- **Validação**: Pydantic para schemas e validação
- **Processamento**: PDFMiner.six + Tesseract para PDFs, LXML para XMLs

## 📋 Pré-requisitos

- Python 3.11+
- PostgreSQL 14+
- Redis 6+
- Tesseract OCR (para processamento de PDFs)

## 🛠️ Instalação

### Opção 1: Setup Automático (Recomendado)

```bash
# Clone o repositório
git clone <url-do-repositorio>
cd project

# Execute o script de setup
python setup_local.py
```

### Opção 2: Setup Manual

```bash
# 1. Ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# 2. Dependências
pip install -r requirements.txt

# 3. Configure o banco PostgreSQL
createdb nfe_system

# 4. Configure o arquivo .env
cp config.local.env .env
# Edite .env com suas configurações

# 5. Migrações e seeds
cd backend
alembic upgrade head
python -c "from app.seeds import executar_seeds; executar_seeds()"
```

## 🚀 Execução

### Desenvolvimento

```bash
# Terminal 1: API FastAPI
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
make migrate       # Executa migrações
make seed          # Popula o banco
make health        # Verifica status dos serviços
make setup         # Setup completo
```

## 📚 Documentação da API

Após iniciar a API, acesse:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🔐 Autenticação

O sistema usa JWT com refresh tokens. Para acessar endpoints protegidos:

1. Faça login em `/auth/login`
2. Use o token retornado no header: `Authorization: Bearer <token>`
3. Use `/auth/refresh` para renovar o token

## 🗄️ Estrutura do Banco

### Tabelas Principais

- **users**: Usuários do sistema com roles
- **fornecedores**: Cadastro de fornecedores
- **materias_primas**: Catálogo de matérias-primas
- **materia_prima_precos**: Histórico de preços
- **notas**: Notas fiscais recebidas
- **nota_itens**: Itens das notas fiscais
- **produtos**: Produtos finais
- **produto_componentes**: Estrutura de BOM
- **produto_precos**: Custos calculados dos produtos
- **audit_logs**: Log de auditoria de todas as alterações

## 🔄 Tarefas Assíncronas

### Celery Tasks

- **Email Processing**: Processamento automático de emails IMAP
- **XML/PDF Parsing**: Extração de dados de notas fiscais
- **Price Updates**: Atualização de preços e recálculo de custos
- **Cost Recalculation**: Recalculação automática de custos de produtos
- **Maintenance**: Limpeza de logs, verificação de integridade

## 📊 Funcionalidades de Negócio

### Conversão de Unidades
- Sistema inteligente de conversão automática
- Exemplos: Rolo → metros, Jogo → unidades
- Configurável via tabela `unidades`

### Cálculo de Custos
- Cálculo automático baseado em BOM
- Recalculação automática quando preços de MP mudam
- Histórico de custos com variações

### Deduplicação
- Verificação de `file_hash` para evitar duplicatas
- Validação de `chave_acesso` única
- Controle de status de processamento

## 🧪 Testes

```bash
# Executar todos os testes
make test

# Executar testes específicos
cd backend
python -m pytest tests/test_api.py -v
python -m pytest tests/test_models.py -v
```

## 📁 Estrutura do Projeto

```
project/
├── backend/                 # Backend FastAPI
│   ├── app/
│   │   ├── api/            # Rotas da API
│   │   ├── auth/           # Autenticação
│   │   ├── models/         # Modelos SQLAlchemy
│   │   ├── schemas/        # Schemas Pydantic
│   │   ├── tasks/          # Tarefas Celery
│   │   └── utils/          # Utilitários
│   ├── alembic/            # Migrações
│   ├── tests/              # Testes
│   └── requirements.txt    # Dependências
├── src/                    # Frontend React (se aplicável)
├── config.local.env        # Configuração de exemplo
├── setup_local.py          # Script de setup
├── Makefile                # Comandos de desenvolvimento
└── README.md               # Este arquivo
```

## 🔧 Configuração

### Ambiente
- `passlib[bcrypt]==1.7.4` e `bcrypt==3.2.2` (instale com `pip install -r requirements.txt`)
- `.env` deve conter `DATABASE_URL` (pooler do Supabase, `sslmode=require`)

### Validação de e-mail (Pydantic v2)
Instale as dependências e verifique:

```bash
pip install -r requirements.txt
python scripts/check_email_validator.py
```

### Variáveis de Ambiente Importantes

1. **Copie o arquivo .env.example para .env e ajuste o host/senha:**
   ```bash
   cp .env.example .env
   ```

2. **Teste a conexão:**
   ```bash
   python scripts/db_smoketest.py
   ```

3. **Rode migrações:**
   ```bash
   cd backend
   alembic upgrade head
   ```

4. **Rode seeds:**
   ```bash
   python -c "from app.seeds import executar_seeds; executar_seeds()"
   ```

### Testes rápidos
```bash
python scripts/db_smoketest.py
cd backend
alembic upgrade head
python -c "from app.seeds import executar_seeds; executar_seeds()"
```

### Configurações Importantes

```env
# Banco de dados (Transaction Pooler - Supabase)
DATABASE_URL=postgresql+psycopg://postgres:<SENHA>@<HOST>:6543/postgres?sslmode=require

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=sua_chave_secreta

# Upload
UPLOAD_DIR=./data/uploads
MAX_FILE_SIZE=10485760
```

## 🚨 Troubleshooting

### Teste de Conexão com Banco

```bash
# Smoke test da conexão com o banco
python scripts/db_smoketest.py

# Verificar status das migrações
cd backend
alembic current
```

### Problemas Comuns

1. **Erro de conexão com PostgreSQL**
   - Verifique se o serviço está rodando
   - Confirme as credenciais no `.env`
   - Execute o smoke test: `python scripts/db_smoketest.py`

2. **Erro de conexão com Redis**
   - Verifique se o Redis está ativo
   - Teste: `redis-cli ping`

3. **Erro de permissão**
   - Verifique as configurações do banco
   - Confirme se o usuário tem acesso ao banco `nfe_system`

### Logs

```bash
# Ver logs da aplicação
make logs

# Ver logs específicos
tail -f logs/app.log
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique a documentação da API em `/docs`
2. Consulte os logs da aplicação
3. Abra uma issue no repositório

## 🎯 Roadmap

- [ ] Interface web completa
- [ ] Relatórios e dashboards
- [ ] Integração com sistemas ERP
- [ ] API para terceiros
- [ ] Sistema de notificações
- [ ] Backup automático
- [ ] Monitoramento e métricas 