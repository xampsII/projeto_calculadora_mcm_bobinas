-- Query para listar todos os produtos que tiveram preços alterados na data de hoje
-- Esta query busca na tabela materia_prima_precos por registros criados hoje

SELECT 
    mp.id as materia_prima_id,
    mp.nome as nome_materia_prima,
    mp.unidade_codigo,
    mpp.valor_unitario as novo_preco,
    mpp.vigente_desde as data_alteracao,
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

-- Query alternativa: buscar preços que começaram a vigorar hoje
-- (mesmo que tenham sido criados em outra data)

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
WHERE DATE(mpp.vigente_desde) = CURRENT_DATE
ORDER BY mpp.vigente_desde DESC, mp.nome;

-- Query para comparar preços: mostrar preço anterior e novo preço
-- para produtos que tiveram alteração hoje

WITH precos_hoje AS (
    SELECT 
        mpp.materia_prima_id,
        mpp.valor_unitario as preco_atual,
        mpp.vigente_desde,
        mpp.created_at,
        ROW_NUMBER() OVER (PARTITION BY mpp.materia_prima_id ORDER BY mpp.vigente_desde DESC) as rn
    FROM materia_prima_precos mpp
    WHERE DATE(mpp.created_at) = CURRENT_DATE
),
preco_anterior AS (
    SELECT 
        mpp.materia_prima_id,
        mpp.valor_unitario as preco_anterior,
        mpp.vigente_ate
    FROM materia_prima_precos mpp
    WHERE mpp.vigente_ate IS NOT NULL
    AND DATE(mpp.vigente_ate) = CURRENT_DATE
)
SELECT 
    mp.id as materia_prima_id,
    mp.nome as nome_materia_prima,
    mp.unidade_codigo,
    ph.preco_atual,
    pa.preco_anterior,
    (ph.preco_atual - pa.preco_anterior) as variacao_absoluta,
    ROUND(((ph.preco_atual - pa.preco_anterior) / pa.preco_anterior * 100), 2) as variacao_percentual,
    ph.vigente_desde as data_alteracao,
    f.nome as fornecedor_nome,
    n.numero as numero_nota
FROM precos_hoje ph
INNER JOIN materias_primas mp ON ph.materia_prima_id = mp.id
LEFT JOIN preco_anterior pa ON ph.materia_prima_id = pa.materia_prima_id
LEFT JOIN materia_prima_precos mpp ON ph.materia_prima_id = mpp.materia_prima_id AND DATE(mpp.created_at) = CURRENT_DATE
LEFT JOIN fornecedor f ON mpp.fornecedor_id = f.id_fornecedor
LEFT JOIN notas n ON mpp.nota_id = n.id
WHERE ph.rn = 1
ORDER BY ph.vigente_desde DESC, mp.nome;
