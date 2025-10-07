# MCP Server Dockerfile
FROM node:18-alpine

WORKDIR /app

# Copiar package.json
COPY package.json ./

# Instalar dependÃªncias
RUN npm install

# Copiar cÃ³digo
COPY . .

# Criar diretÃ³rio para uploads
RUN mkdir -p uploads

# Comando para manter o container rodando
CMD ["node", "index.js"]
