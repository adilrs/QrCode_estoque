# 📦 Guia de Deployment - Sistema de Transferência de Material v1.0

## 🎯 Visão Geral
Este guia fornece instruções completas para instalar e executar o Sistema de Transferência de Material em outro computador.

## 📋 Pré-requisitos

### Software Necessário:
1. **Python 3.8+** - [Download](https://www.python.org/downloads/)
2. **Node.js 16+** - [Download](https://nodejs.org/)
3. **Git** (opcional) - [Download](https://git-scm.com/)

## 🚀 Instalação Passo a Passo

### 1. Transferir os Arquivos

**Opção A: Via Git (Recomendado)**
```bash
git clone <URL_DO_REPOSITORIO>
cd Code\ transf
```

**Opção B: Cópia Manual**
- Copie toda a pasta do projeto para o novo computador
- Mantenha a estrutura de pastas intacta

### 2. Instalação Automática

**Opção A: Instalação Robusta (Mais Compatível) ⭐**
```bash
# Execute o instalador robusto
install_robust.bat
```
- Tenta múltiplos métodos de instalação
- Resolve automaticamente problemas de versão
- Atualiza pip automaticamente
- Fallback para versões alternativas
- Máxima compatibilidade

**Opção B: Instalação Simples (Recomendada)**
```bash
# Execute o instalador simples
install_simple.bat
```
- Usa dependências Python globais
- Mais compatível com diferentes sistemas
- Evita problemas de ambiente virtual

**Opção C: Instalação com Ambiente Virtual**
```bash
# Execute o instalador completo
install.bat
```
- Cria ambiente virtual isolado
- Melhor para desenvolvimento
- Pode ter problemas em alguns sistemas

### 3. Instalação Manual (Se os scripts falharem)

**Backend (Python/Flask):**
```bash
# Navegar para a pasta do projeto
cd "Code transf"

# Instalar dependências globalmente
pip install flask flask-cors pyodbc

# OU criar ambiente virtual
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

**Frontend (React):**
```bash
# Instalar dependências do Node.js
npm install
```

**Certificados SSL:**
```bash
# Gerar certificados SSL
python generate_ssl.py
```

## ⚙️ Configuração

### 1. Banco de Dados
- Edite o arquivo `fdbacc.py` com as credenciais do seu banco
- Configure a string de conexão na linha correspondente

### 2. Portas e URLs
- **Backend**: Porta 5000 (HTTPS)
- **Frontend**: Porta 5173 (HTTPS)
- Certifique-se de que essas portas estejam livres

## 🏃‍♂️ Executando a Aplicação

### Opção A: Inicialização Automática

**Se usou install_robust.bat:**
```bash
# Execute o inicializador robusto
start_robust.bat
```

**Se usou install_simple.bat:**
```bash
# Execute o inicializador simples
start_simple.bat
```

**Se usou install.bat:**
```bash
# Execute o inicializador completo
start_system.bat
```

### Opção B: Inicialização Manual

**1. Iniciar Backend:**
```bash
# Terminal 1 - Backend
python fdbacc.py
```

**2. Iniciar Frontend:**
```bash
# Terminal 2 - Frontend
npm run dev
```

### 3. Acessar a Aplicação
- Abra o navegador em: `https://localhost:5173`
- Aceite o certificado SSL (desenvolvimento)

## 🔧 Solução de Problemas

### Erro no Ambiente Virtual Python
- **Problema**: `Error: Command returned non-zero exit status 1`
- **Causa**: Problemas com criação de ambiente virtual
- **Solução**: Use `install_simple.bat` em vez de `install.bat`
- **Alternativa**: Instale dependências globalmente:
  ```bash
  pip install flask flask-cors pyodbc
  npm install
  ```

### Erro de Certificado SSL
- **Problema**: `net::ERR_CERT_AUTHORITY_INVALID`
- **Solução**: Clique em "Avançado" → "Prosseguir para localhost"

### Erro de Conexão com Banco
- Verifique as credenciais em `fdbacc.py`
- Teste a conectividade com o banco de dados
- Use o botão "Testar Conexão BD" na aplicação

### Porta em Uso
- **Backend**: Altere a porta em `fdbacc.py`
- **Frontend**: Altere em `vite.config.js`

### Dependências em Falta
```bash
# Reinstalar dependências Python
pip install flask flask-cors pyodbc

# Reinstalar dependências Node.js
npm install
```

### Problemas com Caminhos (Espaços no Nome)
- **Problema**: Erro em caminhos com espaços
- **Solução**: Mova o projeto para pasta sem espaços
- **Exemplo**: `C:\projetos\sistema-material\`

### Erro de Versão do Flask
- **Problema**: `ERROR: Could not find a version that satisfies the requirement flask==3.1.2`
- **Causa**: Versão específica do Flask não disponível
- **Solução**: 
  - O arquivo `requirements.txt` foi atualizado para usar Flask 3.0.3
  - Execute novamente o script de instalação
  - Se persistir, instale manualmente: `pip install flask==3.0.3 fdb==2.0.4`
  - Atualize o pip primeiro: `python -m pip install --upgrade pip`

## 📁 Estrutura do Projeto

```
Code transf/
├── 📁 .venv/              # Ambiente virtual Python
├── 📁 src/                # Código fonte React
│   ├── App.jsx           # Componente principal
│   ├── App.css           # Estilos CSS
│   └── ...
├── 📁 public/             # Arquivos públicos
├── 📄 fdbacc.py          # Backend Flask
├── 📄 package.json       # Dependências Node.js
├── 📄 requirements.txt   # Dependências Python
├── 📄 cert.pem          # Certificado SSL
├── 📄 key.pem           # Chave SSL
└── 📄 vite.config.js    # Configuração Vite
```

## 🔒 Segurança

- **Certificados SSL**: Incluídos para desenvolvimento
- **Produção**: Gere novos certificados para ambiente produtivo
- **Banco de Dados**: Configure credenciais seguras

## 📱 Funcionalidades

### ✅ Implementadas na v1.0:
- 📷 Scanner QR Code
- 🔍 Consulta manual de códigos
- 📊 Exibição de dados do material
- 🚚 Sistema de transferência
- 📱 Interface responsiva (mobile)
- 🛡️ Validações de segurança
- 🚫 Bloqueio para materiais sem requisição

### 🎨 Status Visuais:
- 🟢 **Disponível**: Material pronto para transferência
- 🟡 **Pendente**: Material com quantidade recebida
- 🟢 **Transferido**: Material já transferido
- 🔴 **Sem Requisição**: Material bloqueado (sem requisição)

## 📞 Suporte

Em caso de problemas:
1. Verifique os logs no terminal
2. Teste a conexão com banco de dados
3. Confirme se todas as dependências estão instaladas
4. Verifique se as portas estão livres

---

**Sistema de Transferência de Material v1.0** 🚀
*Desenvolvido com React + Flask + TailwindCSS*