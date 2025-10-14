# 📋 INSTRUÇÕES: Exportar Dados do PostgreSQL para o Cliente

## 🎯 Objetivo
Exportar **TODOS os dados** do seu PostgreSQL local para que o cliente tenha os mesmos dados no SQLite.

---

## ✅ MÉTODO 1: Usar pgAdmin (RECOMENDADO)

### Passo 1: Abrir pgAdmin
1. Abra o **pgAdmin 4**
2. Conecte ao servidor **PostgreSQL 17 (porta 5433)**
3. Navegue até: `Servers` → `PostgreSQL 17` → `Databases` → `nfe_system`

### Passo 2: Fazer Backup
1. **Clique com botão direito** em `nfe_system`
2. Selecione **Backup...**
3. Configure:
   - **Filename**: `C:\Users\pplima\Downloads\project\backup-dados.sql`
   - **Format**: `Plain` (SQL text file)
   - **Encoding**: `UTF8`
   
4. Aba **Dump Options**:
   - **Sections**: Marque apenas `Data` ✅ (desmarque `Pre-data` e `Post-data`)
   - **Type of objects**: Marque `Only data` ✅
   - **Do not save**: Desmarque tudo
   - **Queries**: Marque `Use Column inserts` ✅

5. Clique em **Backup**

### Passo 3: Converter para SQLite
Depois que o arquivo `backup-dados.sql` for criado, execute:

```bash
python converter-sql-para-sqlite.py
```

---

## ✅ MÉTODO 2: Linha de Comando (Se o pgAdmin der problema)

### Opção A: Adicionar pg_dump ao PATH

1. Encontre a pasta do PostgreSQL 17:
   ```
   C:\Program Files\PostgreSQL\17\bin
   ```

2. Abra PowerShell como **Administrador** e execute:
   ```powershell
   $env:PATH += ";C:\Program Files\PostgreSQL\17\bin"
   [System.Environment]::SetEnvironmentVariable("PATH", $env:PATH, [System.EnvironmentVariableTarget]::Machine)
   ```

3. **Feche e abra um novo PowerShell** e execute:
   ```powershell
   cd C:\Users\pplima\Downloads\project
   
   $env:PGPASSWORD = "postgres"
   
   & "C:\Program Files\PostgreSQL\17\bin\pg_dump.exe" `
     -h localhost `
     -p 5433 `
     -U postgres `
     -d nfe_system `
     --data-only `
     --column-inserts `
     --no-owner `
     --no-privileges `
     --encoding=UTF8 `
     -f backup-dados.sql
   ```

---

## ✅ MÉTODO 3: Python com pandas (ALTERNATIVA)

Se os métodos acima não funcionarem, execute:

```bash
pip install pandas sqlalchemy psycopg2-binary

python migrar-com-pandas.py
```

---

## 📊 Depois da Exportação

### 1. Verificar o arquivo gerado:
```bash
ls -l backup-dados.sql
```

### 2. Importar para SQLite:
```bash
python importar-sql-para-sqlite.py
```

### 3. Confirmar dados no SQLite:
```bash
python verificar-tabela-precos.py
```

### 4. Commitar e enviar para o cliente:
```bash
git add backend/nfe_system.db
git commit -m "feat: adicionar banco de dados completo com todos os dados"
git push
```

---

## ❓ PROBLEMAS COMUNS

### Erro de encoding
- Use **UTF8** em todas as exportações
- No pgAdmin, sempre selecione `Encoding: UTF8`

### pg_dump não encontrado
- Verifique se o PostgreSQL está instalado
- Adicione a pasta `bin` do PostgreSQL ao PATH

### Tabelas vazias após importação
- Certifique-se de marcar `Only data` no pgAdmin
- Use `--data-only` no pg_dump

---

## 🚀 ATALHO RÁPIDO

Se você tem acesso direto ao PostgreSQL via linha de comando:

```powershell
# Definir senha
$env:PGPASSWORD = "postgres"

# Exportar
pg_dump -h localhost -p 5433 -U postgres -d nfe_system --data-only --column-inserts -f backup-dados.sql

# Converter e importar
python converter-sql-para-sqlite.py
python importar-sql-para-sqlite.py

# Verificar
python verificar-dados-sqlite.py

# Enviar
git add backend/nfe_system.db
git commit -m "feat: banco completo com dados"
git push
```

---

## ℹ️ Informações Técnicas

- **PostgreSQL**: localhost:5433 / nfe_system
- **SQLite**: backend/nfe_system.db
- **Encoding**: UTF-8
- **Formato**: Plain SQL com INSERT por coluna

---

**Próximo passo**: Escolha um dos métodos acima e exporte os dados! 🎯

