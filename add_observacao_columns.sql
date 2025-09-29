-- Script para adicionar coluna observacao nas tabelas de preços
-- Execute este script no pgAdmin

-- Adicionar coluna observacao na tabela materia_prima_precos
ALTER TABLE materia_prima_precos 
ADD COLUMN IF NOT EXISTS observacao VARCHAR(500);

-- Adicionar coluna observacao na tabela produto_precos
ALTER TABLE produto_precos 
ADD COLUMN IF NOT EXISTS observacao VARCHAR(500);

-- Verificar se as colunas foram criadas
SELECT column_name, data_type, character_maximum_length 
FROM information_schema.columns 
WHERE table_name IN ('materia_prima_precos', 'produto_precos')
AND column_name = 'observacao';



