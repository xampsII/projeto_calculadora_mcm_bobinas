# Frontend Dockerfile
FROM node:18-alpine

WORKDIR /app

# Copiar package.json e package-lock.json da raiz do projeto
COPY package*.json ./

# Instalar dependências
RUN npm install

# Copiar arquivos de configuração da raiz
COPY vite.config.ts ./
COPY tsconfig.json ./
COPY tsconfig.app.json ./
COPY tsconfig.node.json ./
COPY index.html ./
COPY postcss.config.js ./
COPY tailwind.config.js ./
COPY eslint.config.js ./

# Copiar código da pasta src
COPY src/ ./src/

# Expor porta
EXPOSE 5173

# Comando para iniciar
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
