# 🔐 Guia da Tela de Login de Teste

## Visão Geral

Esta é uma tela de login separada criada especificamente para testes, **sem alterar o código atual em funcionamento**. A tela permite autenticação de usuários através de uma stored procedure do banco de dados.

## 📍 Acesso

**URL da Tela de Login:** `https://192.168.2.96:5000/login`

## 🎯 Funcionalidades

### 1. **Seleção de Usuário**
- Lista suspensa (dropdown) com usuários pré-definidos
- Usuários disponíveis para teste:
  - **112** - Administrador
  - **113** - Operador
  - **114** - Supervisor
  - **115** - Analista
  - **116** - Gerente

### 2. **Autenticação**
- Campo de senha para inserção manual
- Integração com stored procedure: `Login_pwd(user_id, password)`
- Retorna o código do usuário se autenticação bem-sucedida
- Retorna `null` se credenciais inválidas

### 3. **Gerenciamento de Sessão**
- Armazena código do usuário na sessão
- Persistência da sessão no navegador
- Informações de login (usuário, horário)
- Função de logout

## 🔧 Integração Técnica

### Endpoint de Autenticação
```
POST /api/login_auth
```

**Parâmetros:**
```json
{
  "user_id": "112",
  "password": "010018"
}
```

**Resposta de Sucesso:**
```json
{
  "success": true,
  "auth_code": 112,
  "message": "Login realizado com sucesso"
}
```

**Resposta de Falha:**
```json
{
  "success": false,
  "message": "Credenciais inválidas"
}
```

### Stored Procedure
```sql
select auth from Login_pwd(112, '010018')
```
- **Sucesso**: `auth` = código do usuário (ex: 112)
- **Falha**: `auth` = `null`

## 📊 Log e Auditoria

### Logs Gerados
- **Login bem-sucedido**: `[LOGIN_AUTH] Login bem-sucedido para usuário {id}, auth_code: {code}`
- **Login falhado**: `[LOGIN_AUTH] Falha no login para usuário {id}`
- **Tentativa de login**: `[LOGIN_AUTH] Tentativa de login para usuário: {id}`

### Auditoria
- Todas as tentativas de login são registradas no sistema de auditoria
- Inclui IP do usuário, resultado da autenticação e timestamp

## 🎨 Interface

### Características
- **Design moderno** com gradiente azul/roxo
- **Responsiva** - funciona em desktop e mobile
- **Feedback visual** para sucesso/erro
- **Informações da sessão** após login bem-sucedido
- **Botão de logout** para encerrar sessão

### Estados da Interface
1. **Formulário de Login** - Estado inicial
2. **Autenticando** - Durante processo de login
3. **Sessão Ativa** - Após login bem-sucedido
4. **Mensagens de Erro** - Para credenciais inválidas

## 🔒 Segurança

### Medidas Implementadas
- Validação de entrada no frontend e backend
- Logs de auditoria para todas as tentativas
- Tratamento seguro de erros
- Não exposição de informações sensíveis

## 🚀 Como Usar

### Passo a Passo
1. **Acesse** `https://192.168.2.96:5000/login`
2. **Selecione** um usuário da lista suspensa
3. **Digite** a senha correspondente
4. **Clique** em "Entrar"
5. **Visualize** as informações da sessão se login bem-sucedido
6. **Use** o botão "Sair" para fazer logout

### Exemplo de Teste
- **Usuário**: 112
- **Senha**: 010018 (conforme exemplo da stored procedure)

## 📝 Integração com Sistema Principal

### Código do Usuário na Sessão
Após login bem-sucedido, o código do usuário fica disponível para:
- **JavaScript**: `window.getCurrentUserId()`
- **Sessão**: `window.userSession.userId`
- **LocalStorage**: Persistido automaticamente

### Uso em Outras Partes do Sistema
```javascript
// Obter código do usuário logado
const userId = window.getCurrentUserId();

// Verificar se usuário está logado
if (window.userSession.isLoggedIn) {
    console.log('Usuário logado:', window.userSession.userId);
}
```

## ⚠️ Importante

- **Esta é uma tela de TESTE** - não substitui o sistema principal
- **Não altera** o código atual em funcionamento
- **Isolada** do sistema principal para evitar conflitos
- **Logs separados** para facilitar debugging

## 🔧 Manutenção

### Arquivos Relacionados
- **Frontend**: `login_test.html`
- **Backend**: Endpoint `/api/login_auth` em `fdbacc.py`
- **Rota**: `/login` para servir a página

### Personalização
Para adicionar novos usuários, edite a lista no arquivo `login_test.html`:
```javascript
const users = {
    '112': 'Administrador',
    '113': 'Operador',
    // Adicione novos usuários aqui
};
```

---

**Desenvolvido para testes e validação da funcionalidade de autenticação.**