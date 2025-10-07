# MCP Server Dockerfile
FROM node:18-alpine

WORKDIR /app

# Copiar package.json
COPY package.json ./

# Instalar dependências
RUN npm install

# Copiar código
COPY . .

# Criar diretório para uploads
RUN mkdir -p uploads

# Comando para manter o container rodando
CMD ["node", "index.js"]
