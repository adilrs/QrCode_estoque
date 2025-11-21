# Melhorias na Stored Procedure CONSULTA_QR_MATERIAL

## Problema Original
A procedure original retornava valores nulos para `QT_REC`, o que não fornecia informações suficientes sobre:
- Quanto da requisição já foi baixado
- Quanto ainda precisa ser baixado
- Se a etiqueta atual pode finalizar a requisição

## Solução Implementada

### 1. Novas Variáveis de Controle
```sql
DECLARE VARIABLE QT_JA_BAIXADA DOUBLE PRECISION;
DECLARE VARIABLE QT_REQUISICAO DOUBLE PRECISION;
DECLARE VARIABLE QT_RESTANTE DOUBLE PRECISION;
```

### 2. Cálculo da Quantidade Já Baixada
```sql
select COALESCE(SUM(v2.QUANTIDADE), 0)
from DS_ENTRA_ESTOQUE_VOLS v2
where v2.NREC = :NREQ
  and v2.BAIXADO = 1
  and v2.codigomoldes = :codigomoldes
into QT_JA_BAIXADA;
```

### 3. Lógica de Decisão Inteligente

#### Cenário 1: Quantidade Restante ≤ Quantidade da Etiqueta
```sql
if (QT_RESTANTE <= QT_ETIQ and QT_RESTANTE > 0) then
    QT_REC = QT_RESTANTE;
```
**Resultado**: Retorna exatamente o que falta para completar a requisição

#### Cenário 2: Quantidade Restante > Quantidade da Etiqueta
```sql
else if (QT_RESTANTE > 0) then
    QT_REC = QT_ETIQ;
```
**Resultado**: Retorna a quantidade total da etiqueta (baixa parcial)

#### Cenário 3: Requisição Já Completa
```sql
else
    QT_REC = 0;
```
**Resultado**: Indica que a requisição já foi totalmente atendida

## Benefícios da Melhoria

### 1. **Informação Precisa**
- Frontend recebe exatamente quanto deve ser baixado
- Elimina ambiguidade sobre quantidades

### 2. **Controle de Requisições**
- Sabe quando uma requisição será finalizada
- Previne baixas excessivas

### 3. **Melhor UX**
- Usuário vê claramente o progresso da requisição
- Interface pode mostrar "Finaliza Requisição" vs "Baixa Parcial"

### 4. **Consistência de Dados**
- Garante que requisições não sejam sobre-atendidas
- Mantém integridade entre etiquetas e requisições

## Exemplo Prático

### Requisição 43493: 1.0 KG
- **Etiqueta 1**: 0.3 KG → QT_REC = 0.3 (baixa parcial)
- **Etiqueta 2**: 0.5 KG → QT_REC = 0.5 (baixa parcial)
- **Etiqueta 3**: 0.4 KG → QT_REC = 0.2 (finaliza requisição)
- **Etiqueta 4**: 0.3 KG → QT_REC = 0 (requisição já completa)

## Compatibilidade
- Mantém todas as colunas originais
- Não quebra código existente
- Melhora apenas a lógica de cálculo de `QT_REC`

## Próximos Passos
1. Testar a procedure em ambiente de desenvolvimento
2. Validar com etiquetas das requisições existentes
3. Atualizar frontend para usar a nova informação
4. Implementar em produção