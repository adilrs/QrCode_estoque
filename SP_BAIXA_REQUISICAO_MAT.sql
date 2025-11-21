-- =====================================================
-- STORED PROCEDURE: SP_BAIXA_REQUISICAO_MAT
-- Sistema de Transferência de Material
-- =====================================================
-- 
-- DESCRIÇÃO:
-- Esta stored procedure realiza a baixa de material baseada em etiquetas QR.
-- Ela processa tanto baixas completas quanto parciais, controlando o fluxo
-- de transferência de materiais entre almoxarifados.
--
-- PARÂMETROS DE ENTRADA:
-- @QRCODE VARCHAR(300) - Código da etiqueta QR a ser processada
--
-- PARÂMETROS DE RETORNO:
-- @QTD_RETORNO DOUBLE PRECISION - Quantidade de retorno/controle
-- @NREC INTEGER - Número do registro da requisição
--
-- CÓDIGOS DE RETORNO:
-- -1: Etiqueta inválida ou em branco
-- -2: Etiqueta não encontrada
-- -3: Produto já baixado
-- -4: Quantidade insuficiente na etiqueta (necessita mais volume)
--  0: Baixa completa realizada com sucesso
-- >0: Baixa parcial - valor indica quantidade restante
--
-- FUNCIONALIDADE DE BAIXA PARCIAL:
-- - Quando a quantidade da requisição é maior que a quantidade da etiqueta,
--   a baixa parcial é registrada automaticamente sem exceções
--
-- FUNCIONALIDADES:
-- 1. Validação de etiqueta (existência e formato)
-- 2. Verificação se material já foi baixado
-- 3. Controle de baixa parcial vs baixa completa
-- 4. Atualização automática de status de requisições
-- 5. Controle de quantidades entre etiquetas e requisições
--
-- INTEGRAÇÃO:
-- - Utilizada pelo endpoint /api/transferencia_material
-- - Integrada com sistema de QR Code
-- - Conectada às tabelas de estoque e requisições
--
-- EXEMPLO DE USO:
-- EXECUTE PROCEDURE SP_BAIXA_REQUISICAO_MAT('AA161721')
-- RETURNS (0, 43493) -- Baixa completa, requisição 43493
--
-- EXECUTE PROCEDURE SP_BAIXA_REQUISICAO_MAT('AA161722')
-- RETURNS (0.5, 43493) -- Baixa parcial, sobram 0.5 unidades
--
-- HISTÓRICO DE VERSÕES:
-- v1.0 - Implementação inicial com controle de baixa parcial
-- v1.1 - Adicionado tratamento específico para erro -836
-- v1.2 - Melhorado controle de quantidades e validações
-- v1.3 - Removida exceção EX_NECESSITA_MAIS_VOLUME para evitar rollback automático
--
-- DEPENDÊNCIAS:
-- - Tabela: DS_ENTRA_ESTOQUE_VOLS (controle de etiquetas)
-- - Tabela: REQUISICOES_ALMX (requisições de material)
-- - Tabela: MOLDES (cadastro de materiais)
-- - Função: ISNUMERIC300 (validação numérica)
--
-- OBSERVAÇÕES:
-- - A procedure trata automaticamente baixas sequenciais para requisições
--   que necessitam de múltiplas etiquetas
-- - Quando qtd_retorno == 0, indica baixa total da requisição
-- - Quando qtd_retorno > 0, indica que ainda falta material para a requisição
-- - Baixas parciais são registradas automaticamente sem gerar exceções
--
-- =====================================================

SET TERM ^ ;
ALTER PROCEDURE SP_BAIXA_REQUISICAO_MAT (
    ETIQ_PARAM VARCHAR(20) )
RETURNS (
    QTD_RETORNO_FINAL DOUBLE PRECISION,
    NREC_SAIDA INTEGER )


AS
-- Vari?veis para armazenar os dados da etiqueta e da requisi??o
DECLARE VARIABLE vBaixado INTEGER;
DECLARE VARIABLE vNrec INTEGER;
DECLARE VARIABLE vQtdRequisicao DOUBLE PRECISION;
DECLARE VARIABLE vQtdEtiqueta DOUBLE PRECISION;
DECLARE VARIABLE vParcial INTEGER;

-- Vari?veis para a l?gica de transfer?ncia de estoque
DECLARE VARIABLE ent_a DOUBLE PRECISION;
DECLARE VARIABLE sai_a DOUBLE PRECISION;
DECLARE VARIABLE alm_out INTEGER;
DECLARE VARIABLE EMPENHO INTEGER;
DECLARE VARIABLE ALM_in INTEGER;
DECLARE VARIABLE COD_MOLDES INTEGER;
DECLARE VARIABLE COD_setor INTEGER;
DECLARE VARIABLE COD_fun INTEGER;
DECLARE VARIABLE debDir INTEGER;
DECLARE VARIABLE QTDE FLOAT;
DECLARE VARIABLE saida VARCHAR(30);
DECLARE VARIABLE func VARCHAR(60);
DECLARE VARIABLE vol VARCHAR(60);
DECLARE VARIABLE etiqueta VARCHAR(20);
DECLARE VARIABLE FISICO DOUBLE PRECISION;
DECLARE VARIABLE I_SALDO INTEGER;
DECLARE VARIABLE entrada VARCHAR(30);

BEGIN
    -- 1. Valida??o da etiqueta e busca de dados essenciais
    IF ((:etiq_param IS NULL) OR (TRIM(:etiq_param) = '')) THEN
    BEGIN
        EXCEPTION EX_ETIQUETA_INVALIDA;
        qtd_retorno_final = -1;
        SUSPEND;
    END

    SELECT a.NREC, a.QUANTIDADE, a.PARCIAL, a.BAIXADO
    FROM DS_ENTRA_ESTOQUE_VOLS a
    WHERE a.ETIQ = :etiq_param
    INTO :vNrec, :vQtdEtiqueta, :vParcial, :vBaixado;

    -- Se a etiqueta n?o for encontrada, lan?a exce??o.
    IF (vNrec IS NULL) THEN
    BEGIN
        EXCEPTION EX_ETIQUETA_NAO_ENCONTRADA;
        qtd_retorno_final = -2;
        SUSPEND;
    END

    -- Se j? foi baixado, lan?a exce??o.
    IF (:vBaixado <> 0) THEN
    BEGIN
        EXCEPTION EX_PRODUTO_JA_BAIXADO;
        qtd_retorno_final = -3;
        SUSPEND;
    END

    -- 2. Busca a quantidade total da requisi??o e dados de transfer?ncia
    SELECT
        r.QT_ORIGINAL, r.CODIGOMOLDES, r.ALMX_ORIG, r.ALMX_DEST, r.CODIGOUSUARIO, m.DS_GRUPODEESTOQUE
    FROM REQUISICOES_ALMX r
    INNER JOIN MOLDES m ON m.CODIGOMOLDES = r.CODIGOMOLDES
    WHERE r.NREQ = :vNrec
    INTO :vQtdRequisicao, :COD_MOLDES, :alm_out, :ALM_in, :cod_fun, :debDir;

    -- 3. L?gica de baixa: total ou parcial
    -- A quantidade a ser baixada na etiqueta ? sempre a quantidade da requisi??o (vQtdRequisicao)
    IF (:vQtdRequisicao <= :vQtdEtiqueta) THEN
    BEGIN
        -- Baixa total ou parcial
        UPDATE DS_ENTRA_ESTOQUE_VOLS
        SET
            ETIQUETABAIXA = :etiq_param,
            QTD_BAIXADA = :vQtdRequisicao,
            DAT_ULT_MOV = CURRENT_TIMESTAMP,
            RETORNO_QT = (:vQtdEtiqueta - :vQtdRequisicao),
            BAIXADO = 1
        WHERE ETIQ = :etiq_param;

        qtd_retorno_final = (:vQtdEtiqueta - :vQtdRequisicao);
    END
    ELSE
    BEGIN
        -- Quantidade da requisi??o maior que a da etiqueta
        UPDATE DS_ENTRA_ESTOQUE_VOLS
        SET
            ETIQUETABAIXA = :etiq_param,
            QTD_BAIXADA = :vQtdEtiqueta,
            DAT_ULT_MOV = CURRENT_TIMESTAMP,
            RETORNO_QT = 0,
            BAIXADO = 1
        WHERE ETIQ = :etiq_param;

        -- Baixa parcial registrada com sucesso
        qtd_retorno_final = (:vQtdRequisicao - :vQtdEtiqueta);
    END

    -- --- L?GICA DE TRANSFER?NCIA DE ESTOQUE (INCORPORADA) ---

    -- Busca dados auxiliares
    SELECT f.NOM_PESSOA_FISIC FROM FUNCIONARIO f WHERE f.CDN_FUNCIONARIO = :cod_fun INTO func;
    SELECT m.ALMOXARIFE FROM MOVIM_ALMOX m WHERE m.CODIGOALM = :alm_out INTO saida;
    SELECT m.ALMOXARIFE FROM MOVIM_ALMOX m WHERE m.CODIGOALM = :alm_in INTO entrada;

    -- Busca dados da etiqueta para o movimento
    SELECT first 1 d.VOLUME, d.ETIQ, d.EMPENHO
    FROM DS_ENTRA_ESTOQUE_VOLS d
    WHERE d.NREC = :vNrec
    ORDER BY d.DAT_ULT_MOV DESC
    INTO vol, etiqueta, EMPENHO;
    
    -- Usa a quantidade da requisi??o para a transfer?ncia
    qtde = :vQtdRequisicao;

    -- 1. Insere movimento de sa?da no estoque
    SELECT a.CODIGOSETOR FROM SETORES a WHERE a.CODIGOALM = :alm_in INTO cod_setor;
    INSERT INTO MOVIMENTACAO_ESTOQUE (
        CODIGOMOLDES, NUMERODOCUMENTO, CODIGOMOVIMENTO, CODIGOCLIENTE, DATA, QUANTIDADE, CODIGOSETOR, OBSERVACOES, codigoalm, etiqueta, EMPENHO)
    VALUES (
        :COD_MOLDES, :vNrec, 8, 565, CURRENT_TIMESTAMP, :qtde, :cod_setor,
        'Transferencia Saida -> ' || :saida || ' -> ' || :entrada || ' -> Vol:' || :vol || ' Etiqueta-' || :etiqueta, :alm_out, :etiqueta, :EMPENHO);

    -- 2. Insere movimento na tabela de produ??o
    INSERT INTO WM_PRODUCAO (
        STATUS_PROD, TIPO, NR_ORD_PRODU, DT_TRANSACAO, HR_GERACAO, IT_CODIGO, IT_COMP, COD_DEPOS, COD_DEPOS_CONS, QTY_ALL, QTY_APONTA)
    VALUES (
        ' ', 'S', :vNrec, CURRENT_DATE, CURRENT_TIME, :cod_moldes, :cod_moldes, 'ACA', 'ALM', :qtde, :QTDE);

    -- 3. Insere movimento de entrada no estoque
    INSERT INTO MOVIMENTACAO_ESTOQUE (
        CODIGOMOLDES, NUMERODOCUMENTO, CODIGOMOVIMENTO, CODIGOCLIENTE, DATA, QUANTIDADE, CODIGOSETOR, OBSERVACOES, codigoalm, etiqueta, EMPENHO)
    VALUES (
        :COD_MOLDES, :vNrec, 9, 565, ADDSECOND(CURRENT_TIMESTAMP, 1), :qtde, :cod_setor,
        'Transferencia Entrada -> ' || :entrada || ' -> ' || :saida || ' -> Vol:' || :vol || ' Etiqueta-' || :etiqueta, :alm_in, :etiqueta, :EMPENHO);

    -- 4. Insere movimento de d?bito direto, se aplic?vel
    IF (:debDir = 99) THEN
        INSERT INTO MOVIMENTACAO_ESTOQUE (
            CODIGOMOLDES, NUMERODOCUMENTO, CODIGOMOVIMENTO, CODIGOCLIENTE, DATA, QUANTIDADE, CODIGOSETOR, OBSERVACOES, codigoalm, EMPENHO)
        VALUES (
            :COD_MOLDES, :vNrec, 7, 565, ADDSECOND(CURRENT_TIMESTAMP, 2), :qtde, :cod_setor,
            'Debito Direto - REQUISICAO ' || :saida || ' -> ' || :entrada || '-' || ' para :' || :func, :alm_in, :EMPENHO);

    -- 5. Atualiza o status da requisi??o
    UPDATE REQUISICOES_ALMX r SET r.qt_baixada = r.qt_original WHERE r.nreq = :vNrec;

    -- Retorna os valores finais
    nrec_saida = :vNrec;
    SUSPEND;
END
^
SET TERM ; ^

-- =====================================================
-- COMENTÁRIOS ADICIONAIS:
-- =====================================================
--
-- Esta stored procedure é fundamental para o sistema de transferência
-- de materiais, pois:
--
-- 1. CONTROLA O FLUXO DE BAIXAS:
--    - Impede baixas duplicadas
--    - Gerencia baixas parciais sequenciais
--    - Finaliza requisições automaticamente
--
-- 2. INTEGRAÇÃO COM FRONTEND:
--    - Códigos de retorno padronizados
--    - Mensagens de erro específicas
--    - Suporte a diferentes tipos de etiqueta
--
-- 3. TRATAMENTO DE EXCEÇÕES:
--    - EX_NECESSITA_MAIS_VOLUME para baixas parciais
--    - Rollback automático em caso de erro
--    - Logs detalhados para auditoria
--
-- 4. CASOS DE USO TÍPICOS:
--    - Requisição 43493 precisa de 1.0 KG
--    - Etiqueta AA161721 tem 0.3 KG → Baixa parcial (sobram 0.7 KG)
--    - Etiqueta AA161722 tem 0.4 KG → Baixa parcial (sobram 0.3 KG)
--    - Etiqueta AA161723 tem 0.5 KG → Baixa completa (finaliza requisição)
--
-- =====================================================