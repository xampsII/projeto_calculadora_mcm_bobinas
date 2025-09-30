-- Verificar se existem registros na tabela materia_prima_precos
SELECT COUNT(*) as total_registros FROM materia_prima_precos;

-- Verificar registros criados hoje
SELECT COUNT(*) as registros_hoje FROM materia_prima_precos 
WHERE DATE(created_at) = CURRENT_DATE;

-- Verificar registros criados nos últimos 7 dias
SELECT 
    DATE(created_at) as data,
    COUNT(*) as quantidade
FROM materia_prima_precos 
WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY DATE(created_at)
ORDER BY data DESC;

-- Verificar os últimos 10 registros criados
SELECT 
    mp.nome as materia_prima,
    mpp.valor_unitario,
    mpp.created_at,
    mpp.vigente_desde,
    f.nome as fornecedor
FROM materia_prima_precos mpp
LEFT JOIN materias_primas mp ON mpp.materia_prima_id = mp.id
LEFT JOIN fornecedor f ON mpp.fornecedor_id = f.id_fornecedor
ORDER BY mpp.created_at DESC
LIMIT 10;

-- Verificar se há registros com vigente_desde de hoje
SELECT COUNT(*) as registros_vigencia_hoje 
FROM materia_prima_precos 
WHERE DATE(vigente_desde) = CURRENT_DATE;

-- Query mais flexível: buscar registros dos últimos 3 dias
SELECT 
    mp.id as materia_prima_id,
    mp.nome as nome_materia_prima,
    mp.unidade_codigo,
    mpp.valor_unitario as novo_preco,
    mpp.vigente_desde as data_alteracao,
    mpp.created_at as data_criacao,
    f.nome as fornecedor_nome,
    n.numero as numero_nota
FROM materia_prima_precos mpp
INNER JOIN materias_primas mp ON mpp.materia_prima_id = mp.id
LEFT JOIN fornecedor f ON mpp.fornecedor_id = f.id_fornecedor
LEFT JOIN notas n ON mpp.nota_id = n.id
WHERE mpp.created_at >= CURRENT_DATE - INTERVAL '3 days'
ORDER BY mpp.created_at DESC;
