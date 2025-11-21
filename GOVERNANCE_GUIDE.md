# 📋 Guia de Governança de Código

## 🎯 Visão Geral

Este projeto implementa um sistema completo de governança de código que garante qualidade, segurança e consistência no desenvolvimento. O sistema inclui:

- **Padrões obrigatórios** definidos em `.development-standards.json`
- **Validação automática** via `validate_standards.py`
- **Git Hooks** para aplicação automática dos padrões
- **Templates de PR** com checklists de code review

## 🚀 Configuração Inicial

### 1. Ativar Sistema de Governança

```bash
# Configurar Git Hooks automáticos
python setup_git_hooks.py --setup

# Testar configuração
python setup_git_hooks.py --test
```

### 2. Validar Projeto Atual

```bash
# Executar validação completa
python validate_standards.py

# Gerar relatório detalhado
python validate_standards.py --report validation_report.json

# Modo estrito (falha com avisos)
python validate_standards.py --strict
```

## 📋 Padrões Obrigatórios

### 🐍 Python

#### Estrutura de Arquivo
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Descrição do módulo
"""

import os
import sys
from typing import Optional, Dict, Any

# Seu código aqui
```

#### Regras de Qualidade
- **Encoding:** UTF-8 obrigatório
- **Comprimento de linha:** Máximo 120 caracteres
- **Indentação:** 4 espaços
- **Docstrings:** Estilo Google para funções públicas
- **Type hints:** Obrigatório para funções

### 🔒 Segurança

#### ❌ Proibido
```python
# NUNCA faça isso
password = "minha_senha_secreta"  # ❌
api_key = "abc123"               # ❌
query = f"SELECT * FROM users WHERE id = {user_id}"  # ❌
```

#### ✅ Correto
```python
# Sempre faça assim
password = os.getenv('DB_PASSWORD')  # ✅
api_key = os.environ.get('API_KEY')  # ✅
query = "SELECT * FROM users WHERE id = ?"  # ✅
cursor.execute(query, (user_id,))
```

### 🗄️ SQL

#### Estrutura de Procedure
```sql
-- ==============================================
-- Procedure: SP_CONSULTAR_MATERIAL
-- Descrição: Consulta informações de material
-- Autor: [Nome]
-- Data: [Data]
-- Versão: 1.0
-- ==============================================

CREATE OR ALTER PROCEDURE SP_CONSULTAR_MATERIAL(
    P_CODIGO VARCHAR(20)
)
RETURNS (
    DESCRICAO VARCHAR(100),
    ESTOQUE DECIMAL(15,3)
)
AS
BEGIN
    -- Lógica da procedure
END
```

## 🔄 Fluxo de Desenvolvimento

### 🏗️ Regra Fundamental: Ambiente de Homologação

**OBRIGATÓRIO:** Toda implementação deve ser feita primeiro no ambiente de homologação antes de ser migrada para produção.

```bash
# 1. Desenvolver e testar em homologação
cd homologacao/
python fdbacc_homolog.py

# 2. Executar testes completos
python test_homolog_service.py

# 3. Validar com dados reais
# 4. Apenas após aprovação, migrar para produção
```

**Benefícios:**
- ✅ Reduz riscos em produção
- ✅ Permite testes com dados reais
- ✅ Facilita rollback se necessário
- ✅ Garante qualidade antes do deploy

### 1. Antes de Commitar

```bash
# O hook pre-commit executará automaticamente:
# - Validação de padrões
# - Verificação de segurança
# - Análise de qualidade

git add .
git commit -m "feat(api): adicionar endpoint de consulta"
```

### 2. Formato de Commit

```bash
# Formato obrigatório: tipo(escopo): descrição

# Tipos válidos:
feat(api): adicionar novo endpoint        # Nova funcionalidade
fix(db): corrigir erro de conexão         # Correção de bug
docs(readme): atualizar documentação      # Documentação
test(unit): adicionar testes unitários    # Testes
refactor(auth): melhorar autenticação     # Refatoração
style(css): ajustar formatação            # Estilo
chore(deps): atualizar dependências       # Manutenção
```

### 3. Antes de Push

```bash
# O hook pre-push executará:
# - Todos os testes
# - Validação final de padrões
# - Verificação de qualidade

git push origin feature/nova-funcionalidade
```

### 4. Pull Request

Ao criar um PR, use o template automático que inclui:
- Checklist de code review
- Validações de segurança
- Critérios de aprovação
- Documentação necessária

## 🧪 Testes e Validação

### Executar Validações Manuais

```bash
# Validação completa
python validate_standards.py

# Apenas arquivos específicos
python validate_standards.py --path src/

# Com relatório JSON
python validate_standards.py --report report.json
```

### Interpretar Resultados

```
🔍 Validando padrões de desenvolvimento...
📁 Projeto: C:\Code transf
📋 Padrões: Sistema de Transferência v1.0.0
============================================================

📊 Resumo da Validação:
   Arquivos verificados: 25
   Violações críticas: 0
   Avisos: 2

✅ Padrões críticos atendidos (com avisos)
```

## 🛠️ Ferramentas Recomendadas

### Python
```bash
# Instalar ferramentas de qualidade
pip install flake8 black isort pytest coverage bandit safety

# Configurar no projeto
flake8 --max-line-length=120 .
black --line-length=120 .
isort .
```

### Análise de Segurança
```bash
# Verificar vulnerabilidades
bandit -r .
safety check
```

## 🚨 Resolução de Problemas

### Violações Comuns

#### 1. Encoding Ausente
```python
# ❌ Problema
# Arquivo sem declaração de encoding

# ✅ Solução
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
```

#### 2. Senhas Hardcoded
```python
# ❌ Problema
DB_PASSWORD = "senha123"

# ✅ Solução
DB_PASSWORD = os.getenv('DB_PASSWORD', 'default_dev_password')
```

#### 3. SQL Injection
```python
# ❌ Problema
query = f"SELECT * FROM users WHERE name = '{name}'"

# ✅ Solução
query = "SELECT * FROM users WHERE name = ?"
cursor.execute(query, (name,))
```

### Desabilitar Validações (Emergência)

```bash
# Remover hooks temporariamente
python setup_git_hooks.py --remove

# Commit de emergência
git commit --no-verify -m "hotfix: correção crítica"

# Reativar hooks
python setup_git_hooks.py --setup
```

## 📊 Métricas e Monitoramento

### Relatórios Automáticos

O sistema gera métricas sobre:
- Cobertura de testes
- Frequência de deploy
- Tempo de lead
- Taxa de falhas
- Tempo de recuperação

### Dashboard de Qualidade

```bash
# Gerar relatório semanal
python validate_standards.py --report weekly_report.json

# Analisar tendências
python analyze_metrics.py --period weekly
```

## 🎯 Benefícios do Sistema

### ✅ Para Desenvolvedores
- **Feedback imediato** sobre qualidade do código
- **Padrões claros** e automatizados
- **Redução de bugs** em produção
- **Processo de review** mais eficiente

### ✅ Para o Projeto
- **Qualidade consistente** em todo o codebase
- **Segurança aprimorada** com validações automáticas
- **Manutenibilidade** melhorada
- **Onboarding** mais rápido de novos desenvolvedores

### ✅ Para Produção
- **Menos bugs** chegam à produção
- **Deploys mais seguros** com validações
- **Rollbacks** mais rápidos quando necessário
- **Conformidade** com padrões de segurança

## 🔧 Personalização

### Modificar Padrões

Edite `.development-standards.json` para:
- Adicionar novas regras
- Modificar limites (ex: comprimento de linha)
- Configurar exceções
- Ajustar ferramentas

### Adicionar Validações

Extenda `validate_standards.py` para:
- Novas linguagens
- Regras específicas do projeto
- Integrações com ferramentas externas

## 📞 Suporte

Para dúvidas ou problemas:
1. Consulte este guia
2. Execute `python validate_standards.py --help`
3. Verifique os logs de validação
4. Contate a equipe de desenvolvimento

---

**Versão:** 1.0.0  
**Última atualização:** 2025-01-09  
**Responsável:** Equipe de Desenvolvimento