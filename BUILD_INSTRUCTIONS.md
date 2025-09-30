# 🚀 Instruções para Gerar Executável do Sistema NFE

## 📋 Pré-requisitos

### Para o Backend:
- Python 3.8+ instalado
- PostgreSQL instalado e rodando
- Dependências do projeto instaladas

### Para o Frontend:
- Node.js 16+ instalado
- npm instalado

## 🔧 Passo a Passo

### 1. Preparar o Ambiente

```bash
# Instalar dependências do backend
cd backend
pip install -r requirements.txt

# Instalar dependências do frontend
cd ../src
npm install
cd ..
```

### 2. Gerar Executável do Backend

```bash
# Executar script de build do backend
python build_executable.py
```

Este script irá:
- Instalar PyInstaller automaticamente
- Gerar o executável `nfe_backend.exe`
- Criar script de inicialização `start_server.bat`

### 3. Gerar Build do Frontend

```bash
# Executar script de build do frontend
python build_frontend.py
```

Este script irá:
- Instalar dependências do npm
- Gerar build de produção
- Criar script de servidor `serve_frontend.bat`

### 4. Criar Pacote Completo

```bash
# Gerar pacote de deployment
python build_complete.py
```

Este script irá:
- Criar pasta `nfe_deployment/` com todos os arquivos
- Gerar script de instalação automática `install.bat`
- Criar documentação `README.txt`

## 📁 Estrutura Final

```
nfe_deployment/
├── nfe_backend.exe          # Executável do backend
├── start_server.bat         # Script para iniciar backend
├── frontend/                # Arquivos do frontend
│   ├── index.html
│   ├── assets/
│   └── ...
├── serve_frontend.bat       # Script para servir frontend
├── install.bat              # Instalador automático
└── README.txt               # Instruções de uso
```

## 🚀 Como Usar em Outra Máquina

### Opção 1: Instalação Automática
1. Copie a pasta `nfe_deployment/` completa
2. Execute `install.bat`
3. O sistema iniciará automaticamente

### Opção 2: Instalação Manual
1. Copie a pasta `nfe_deployment/` completa
2. Execute `start_server.bat` (para iniciar o backend)
3. Execute `serve_frontend.bat` (para servir o frontend)
4. Acesse http://localhost:8080

## ⚠️ Requisitos na Máquina de Destino

- **Windows 10/11**
- **PostgreSQL** instalado e rodando
- **Python** (para servir o frontend)
- **Conexão com internet** (para dependências)

## 🔧 Configuração do Banco de Dados

1. Instale o PostgreSQL
2. Crie um banco de dados
3. Configure as variáveis de ambiente se necessário
4. Execute as migrações do Alembic

## 🐛 Solução de Problemas

### Erro: "Executável não encontrado"
- Verifique se o build foi executado com sucesso
- Execute os scripts de build na ordem correta

### Erro: "PostgreSQL não encontrado"
- Instale o PostgreSQL na máquina de destino
- Certifique-se de que o serviço está rodando

### Erro: "Porta já em uso"
- Verifique se as portas 8000 e 8080 estão livres
- Pare outros serviços que possam estar usando essas portas

### Erro: "Dependências não encontradas"
- Certifique-se de que há conexão com internet
- O PyInstaller baixará as dependências automaticamente

## 📞 Suporte

Em caso de problemas:
1. Verifique os logs de erro
2. Confirme que todos os requisitos estão instalados
3. Teste os componentes individualmente
4. Verifique a documentação do README.txt

## 🎯 Resultado Final

Após seguir todos os passos, você terá:
- ✅ Executável standalone do backend
- ✅ Frontend otimizado para produção
- ✅ Scripts de inicialização automática
- ✅ Pacote completo para deployment
- ✅ Documentação de uso

O sistema estará pronto para ser executado em qualquer máquina Windows com os requisitos mínimos!
