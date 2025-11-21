# Pull Request

## 📋 Descrição
<!-- Descreva brevemente as mudanças implementadas -->

## 🎯 Tipo de Mudança
<!-- Marque o tipo de mudança -->
- [ ] 🐛 Bug fix (correção que resolve um problema)
- [ ] ✨ Nova funcionalidade (mudança que adiciona funcionalidade)
- [ ] 💥 Breaking change (mudança que quebra compatibilidade)
- [ ] 📚 Documentação (mudanças apenas na documentação)
- [ ] 🎨 Refatoração (mudança que não adiciona funcionalidade nem corrige bugs)
- [ ] ⚡ Performance (mudança que melhora performance)
- [ ] 🧪 Testes (adição ou correção de testes)
- [ ] 🔧 Configuração (mudanças em arquivos de configuração)

## 🔗 Issues Relacionadas
<!-- Liste as issues que este PR resolve -->
Resolve #(número da issue)

## 🧪 Como Testar
<!-- Descreva os passos para testar as mudanças -->
1. 
2. 
3. 

## 📸 Screenshots (se aplicável)
<!-- Adicione screenshots para mudanças visuais -->

## ✅ Checklist de Code Review

### 🎯 Funcionalidade
- [ ] O código implementa corretamente os requisitos?
- [ ] Os casos de erro estão tratados adequadamente?
- [ ] A lógica de negócio está correta?
- [ ] As validações de entrada estão implementadas?

### 🏗️ Qualidade
- [ ] O código está legível e bem estruturado?
- [ ] As funções têm responsabilidade única?
- [ ] Os nomes de variáveis e funções são descritivos?
- [ ] O código segue os padrões de estilo do projeto?
- [ ] Não há código duplicado desnecessário?

### 🔒 Segurança
- [ ] Não há senhas ou chaves hardcoded?
- [ ] As entradas são validadas adequadamente?
- [ ] Queries SQL usam parâmetros (não concatenação)?
- [ ] Não há vulnerabilidades de segurança evidentes?
- [ ] Logs não expõem informações sensíveis?

### ⚡ Performance
- [ ] O código é eficiente?
- [ ] Não há loops desnecessários ou ineficientes?
- [ ] Conexões de banco são fechadas adequadamente?
- [ ] Não há vazamentos de memória evidentes?
- [ ] Operações custosas são otimizadas?

### 🧪 Testes
- [ ] Existem testes para a nova funcionalidade?
- [ ] Os testes cobrem casos de erro?
- [ ] Todos os testes estão passando?
- [ ] Testes de integração foram considerados?
- [ ] Cobertura de testes é adequada?

### 📚 Documentação
- [ ] Código complexo está comentado?
- [ ] Funções públicas têm docstrings?
- [ ] README foi atualizado (se necessário)?
- [ ] Documentação da API foi atualizada (se aplicável)?

### 🔄 Compatibilidade
- [ ] Mudanças são compatíveis com versões anteriores?
- [ ] Migrações de banco foram consideradas?
- [ ] Dependências foram atualizadas adequadamente?
- [ ] Configurações de ambiente foram documentadas?

## 🚀 Checklist de Deploy

### 🧪 Ambiente de Homologação
- [ ] Testado em ambiente de homologação?
- [ ] Funcionalidades validadas com dados reais?
- [ ] Performance testada?
- [ ] Rollback testado?

### 🏭 Produção
- [ ] Backup realizado antes do deploy?
- [ ] Plano de rollback definido?
- [ ] Monitoramento configurado?
- [ ] Equipe notificada sobre o deploy?

## 📝 Notas Adicionais
<!-- Informações adicionais para os revisores -->

## 🔍 Validação Automática
<!-- Este PR passou pelas seguintes validações automáticas -->
- [ ] ✅ Padrões de código validados
- [ ] ✅ Testes automatizados passaram
- [ ] ✅ Verificação de segurança executada
- [ ] ✅ Análise de qualidade de código

---

### 📋 Para Revisores

**Prioridade de Review:**
- 🔴 Alta (crítico/hotfix)
- 🟡 Média (funcionalidade normal)
- 🟢 Baixa (documentação/refatoração)

**Tempo Estimado de Review:** ___ minutos

**Áreas de Foco:**
<!-- Indique áreas específicas que precisam de atenção especial -->
- [ ] Lógica de negócio
- [ ] Segurança
- [ ] Performance
- [ ] Testes
- [ ] Documentação

### 🎯 Critérios de Aprovação

Este PR pode ser aprovado quando:
- [ ] Todos os itens do checklist foram verificados
- [ ] Pelo menos 1 revisor aprovou
- [ ] Todos os testes automatizados passaram
- [ ] Não há conflitos de merge
- [ ] Validação de padrões passou

---

**Autor:** @<!-- seu_usuario -->
**Revisor(es):** @<!-- revisor1 --> @<!-- revisor2 -->
**Data:** <!-- data_atual -->