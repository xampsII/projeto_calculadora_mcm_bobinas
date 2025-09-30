-- Query para listar matérias-primas que tiveram preços atualizados hoje
-- Mostra o preço anterior e o novo preço

WITH precos_atuais AS (
    -- Buscar preços atuais (vigente_ate IS NULL)
    SELECT 
        materia_prima_id,
        valor_unitario as preco_atual,
        vigente_desde,
        created_at,
        fornecedor_id,
        nota_id
    FROM materia_prima_precos
    WHERE vigente_ate IS NULL
),
precos_anteriores AS (
    -- Buscar preços que foram finalizados hoje
    SELECT 
        materia_prima_id,
        valor_unitario as preco_anterior,
        vigente_ate,
        created_at
    FROM materia_prima_precos
    WHERE vigente_ate IS NOT NULL
    AND DATE(vigente_ate) = CURRENT_DATE
),
precos_criados_hoje AS (
    -- Buscar preços criados hoje
    SELECT 
        materia_prima_id,
        valor_unitario as novo_preco,
        vigente_desde,
        created_at,
        fornecedor_id,
        nota_id
    FROM materia_prima_precos
    WHERE DATE(created_at) = CURRENT_DATE
)
SELECT 
    mp.id as materia_prima_id,
    mp.nome as nome_materia_prima,
    mp.unidade_codigo,
    pa.preco_anterior,
    pc.novo_preco,
    (pc.novo_preco - pa.preco_anterior) as variacao_absoluta,
    ROUND(((pc.novo_preco - pa.preco_anterior) / pa.preco_anterior * 100), 2) as variacao_percentual,
    pc.vigente_desde as data_inicio_novo_preco,
    pa.vigente_ate as data_fim_preco_anterior,
    f.nome as fornecedor_nome,
    f.cnpj as fornecedor_cnpj,
    n.numero as numero_nota,
    n.serie as serie_nota,
    n.emissao_date as data_emissao_nota
FROM precos_criados_hoje pc
INNER JOIN materias_primas mp ON pc.materia_prima_id = mp.id
LEFT JOIN precos_anteriores pa ON pc.materia_prima_id = pa.materia_prima_id
LEFT JOIN fornecedor f ON pc.fornecedor_id = f.id_fornecedor
LEFT JOIN notas n ON pc.nota_id = n.id
ORDER BY pc.created_at DESC, mp.nome;

-- Query alternativa mais simples: buscar apenas preços criados hoje
-- (assumindo que se foi criado hoje, é uma atualização)

SELECT 
    mp.id as materia_prima_id,
    mp.nome as nome_materia_prima,
    mp.unidade_codigo,
    mpp.valor_unitario as novo_preco,
    mpp.vigente_desde as data_inicio_vigencia,
    mpp.created_at as data_criacao,
    f.nome as fornecedor_nome,
    f.cnpj as fornecedor_cnpj,
    n.numero as numero_nota,
    n.serie as serie_nota,
    n.emissao_date as data_emissao_nota
FROM materia_prima_precos mpp
INNER JOIN materias_primas mp ON mpp.materia_prima_id = mp.id
LEFT JOIN fornecedor f ON mpp.fornecedor_id = f.id_fornecedor
LEFT JOIN notas n ON mpp.nota_id = n.id
WHERE DATE(mpp.created_at) = CURRENT_DATE
ORDER BY mpp.created_at DESC, mp.nome;

-- Query para ver histórico de preços de uma matéria-prima específica
-- (substitua 'ID_DA_MATERIA_PRIMA' pelo ID desejado)

SELECT 
    mp.nome as materia_prima,
    mpp.valor_unitario,
    mpp.vigente_desde,
    mpp.vigente_ate,
    mpp.created_at,
    f.nome as fornecedor,
    n.numero as nota_fiscal,
    CASE 
        WHEN mpp.vigente_ate IS NULL THEN 'ATUAL'
        ELSE 'HISTÓRICO'
    END as status
FROM materia_prima_precos mpp
INNER JOIN materias_primas mp ON mpp.materia_prima_id = mp.id
LEFT JOIN fornecedor f ON mpp.fornecedor_id = f.id_fornecedor
LEFT JOIN notas n ON mpp.nota_id = n.id
WHERE mp.id = 1  -- Substitua pelo ID da matéria-prima
ORDER BY mpp.vigente_desde DESC;
