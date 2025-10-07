#!/bin/bash

echo "========================================"
echo "    TESTE DO DOCKER - SISTEMA MCM"
echo "========================================"
echo

echo "[1/6] Verificando Docker..."
if ! command -v docker &> /dev/null; then
    echo "ERRO: Docker não encontrado! Instale o Docker primeiro."
    exit 1
fi
docker --version

echo "[2/6] Verificando Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    echo "ERRO: Docker Compose não encontrado!"
    exit 1
fi
docker-compose --version

echo "[3/6] Verificando arquivos necessários..."
if [ ! -f "docker-compose.yml" ]; then
    echo "ERRO: Arquivo docker-compose.yml não encontrado!"
    exit 1
fi

if [ ! -f "package.json" ]; then
    echo "ERRO: Arquivo package.json não encontrado!"
    exit 1
fi

if [ ! -f "backend/Dockerfile" ]; then
    echo "ERRO: Dockerfile do backend não encontrado!"
    exit 1
fi

if [ ! -f "src/Dockerfile" ]; then
    echo "ERRO: Dockerfile do frontend não encontrado!"
    exit 1
fi

echo "[4/6] Verificando portas..."
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null; then
    echo "AVISO: Porta 8000 já está em uso!"
fi

if lsof -Pi :5173 -sTCP:LISTEN -t >/dev/null; then
    echo "AVISO: Porta 5173 já está em uso!"
fi

if lsof -Pi :5432 -sTCP:LISTEN -t >/dev/null; then
    echo "AVISO: Porta 5432 já está em uso!"
fi

echo "[5/6] Limpando cache do Docker..."
docker-compose down >/dev/null 2>&1
docker system prune -f >/dev/null 2>&1

echo "[6/6] Iniciando Docker Compose..."
echo
echo "========================================"
echo "    INICIANDO CONSTRUÇÃO DOS CONTAINERS"
echo "========================================"
echo
echo "Aguarde alguns minutos enquanto os containers são construídos..."
echo

docker-compose up --build

echo
echo "========================================"
echo "    CONSTRUÇÃO FINALIZADA"
echo "========================================"
echo
echo "Se tudo funcionou corretamente:"
echo "- Frontend: http://localhost:5173"
echo "- Backend: http://localhost:8000"
echo
