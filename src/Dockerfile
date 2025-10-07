# Frontend Dockerfile
FROM node:18-alpine

WORKDIR /app

# Copiar package.json e package-lock.json da raiz do projeto
COPY package*.json ./

# Instalar dependências
RUN npm install

# Copiar código da pasta src
COPY src/ .

# Expor porta
EXPOSE 5173

# Comando para iniciar
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
