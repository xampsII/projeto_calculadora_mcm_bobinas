#!/bin/bash

echo "========================================"
echo "    MCM Bobinas - Setup Docker"
echo "========================================"
echo

echo "Verificando se Docker estÃ¡ instalado..."
if ! command -v docker &> /dev/null; then
    echo "ERRO: Docker nÃ£o estÃ¡ instalado"
    echo "Instale Docker em: https://docs.docker.com/get-docker/"
    exit 1
fi

echo "Docker encontrado!"
echo

echo "Verificando se Docker Compose estÃ¡ disponÃ­vel..."
if ! command -v docker-compose &> /dev/null; then
    echo "ERRO: Docker Compose nÃ£o estÃ¡ disponÃ­vel"
    exit 1
fi

echo "Docker Compose encontrado!"
echo

echo "Iniciando aplicaÃ§Ã£o..."
echo "Isso pode levar alguns minutos na primeira execuÃ§Ã£o..."
echo

docker-compose up --build

echo
echo "AplicaÃ§Ã£o finalizada."
