-- Query para listar matérias-primas que tiveram preços atualizados hoje
-- Usando a coluna updated_at em vez de created_at

-- Query principal usando updated_at
SELECT 
    mp.id as materia_prima_id,
    mp.nome as nome_materia_prima,
    mp.unidade_codigo,
    mpp.valor_unitario as novo_preco,
    mpp.vigente_desde as data_inicio_vigencia,
    mpp.created_at as data_criacao,
    mpp.updated_at as data_atualizacao,
    f.nome as fornecedor_nome,
    f.cnpj as fornecedor_cnpj,
    n.numero as numero_nota,
    n.serie as serie_nota,
    n.emissao_date as data_emissao_nota
FROM materia_prima_precos mpp
INNER JOIN materias_primas mp ON mpp.materia_prima_id = mp.id
LEFT JOIN fornecedor f ON mpp.fornecedor_id = f.id_fornecedor
LEFT JOIN notas n ON mpp.nota_id = n.id
WHERE DATE(mpp.updated_at) = CURRENT_DATE
ORDER BY mpp.updated_at DESC, mp.nome;

-- Query alternativa: buscar registros atualizados nos últimos 3 dias
SELECT 
    mp.id as materia_prima_id,
    mp.nome as nome_materia_prima,
    mp.unidade_codigo,
    mpp.valor_unitario as novo_preco,
    mpp.vigente_desde as data_inicio_vigencia,
    mpp.created_at as data_criacao,
    mpp.updated_at as data_atualizacao,
    f.nome as fornecedor_nome,
    f.cnpj as fornecedor_cnpj,
    n.numero as numero_nota,
    n.serie as serie_nota,
    n.emissao_date as data_emissao_nota
FROM materia_prima_precos mpp
INNER JOIN materias_primas mp ON mpp.materia_prima_id = mp.id
LEFT JOIN fornecedor f ON mpp.fornecedor_id = f.id_fornecedor
LEFT JOIN notas n ON mpp.nota_id = n.id
WHERE mpp.updated_at >= CURRENT_DATE - INTERVAL '3 days'
ORDER BY mpp.updated_at DESC, mp.nome;

-- Query para verificar se a coluna updated_at existe e tem dados
SELECT 
    COUNT(*) as total_registros,
    COUNT(updated_at) as registros_com_updated_at,
    MIN(updated_at) as primeira_atualizacao,
    MAX(updated_at) as ultima_atualizacao
FROM materia_prima_precos;

-- Query para ver os últimos registros atualizados
SELECT 
    mp.nome as materia_prima,
    mpp.valor_unitario,
    mpp.created_at,
    mpp.updated_at,
    f.nome as fornecedor
FROM materia_prima_precos mpp
LEFT JOIN materias_primas mp ON mpp.materia_prima_id = mp.id
LEFT JOIN fornecedor f ON mpp.fornecedor_id = f.id_fornecedor
ORDER BY mpp.updated_at DESC NULLS LAST
LIMIT 10;
