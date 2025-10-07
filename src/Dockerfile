# Frontend Dockerfile
FROM node:18-alpine

WORKDIR /app

# Copiar package.json e package-lock.json
COPY package*.json ./

# Instalar dependÃªncias
RUN npm install

# Copiar cÃ³digo
COPY . .

# Expor porta
EXPOSE 5173

# Comando para iniciar
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
