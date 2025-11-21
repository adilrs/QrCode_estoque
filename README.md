# 🚚 Sistema de Transferência de Material v1.0

## 📋 Descrição
Sistema web para leitura de QR codes e transferência de materiais, desenvolvido com React + Flask.

## 🚀 Instalação Rápida (Windows)

### Robusto (Mais Compatível) ⭐
```bash
# Clone ou baixe o projeto
# Execute o instalador robusto (tenta múltiplos métodos)
install_robust.bat

# Inicie o sistema
start_robust.bat
```

### Simples (Recomendado)
```bash
# Execute o instalador simples
install_simple.bat

# Inicie o sistema
start_simple.bat
```

### Com Ambiente Virtual
```bash
# Execute o instalador completo
install.bat

# Inicie o sistema
start_system.bat
```

### Manual
Consulte o [Guia de Deployment](DEPLOYMENT_GUIDE.md) para instruções detalhadas.

## 🎯 Funcionalidades

- 📷 **Scanner QR Code**: Leitura automática via câmera
- 🔍 **Consulta Manual**: Busca por código digitado
- 📊 **Dados do Material**: Visualização completa das informações
- 🚚 **Sistema de Transferência**: Transferência segura de materiais
- 📱 **Interface Responsiva**: Otimizada para mobile e desktop
- 🛡️ **Validações de Segurança**: Bloqueios automáticos

## 🎨 Status dos Materiais

| Status | Cor | Descrição |
|--------|-----|-----------||
| 🟢 Disponível | Verde | Pronto para transferência |
| 🟡 Pendente | Amarelo | Com quantidade recebida |
| 🟢 Transferido | Verde | Já transferido |
| 🔴 Sem Requisição | Vermelho | Bloqueado (sem requisição) |

## 🔧 Tecnologias

- **Frontend**: React 18 + Vite + TailwindCSS
- **Backend**: Flask + Python
- **QR Scanner**: html5-qrcode
- **SSL**: Certificados auto-assinados

## 📁 Estrutura

```
├── 📁 src/                # Frontend React
├── 📄 fdbacc.py          # Backend Flask
├── 📄 install.bat        # Instalador automático
├── 📄 start_system.bat   # Inicializador
├── 📄 DEPLOYMENT_GUIDE.md # Guia completo
└── 📄 requirements.txt   # Dependências Python
```

## 🚀 Início Rápido

1. **Clone/Copie** o projeto
2. **Execute** `install.bat` (Windows)
3. **Inicie** com `start_system.bat`
4. **Acesse** `https://localhost:5173`

## 📞 Suporte

Em caso de problemas, consulte:
- [Guia de Deployment](DEPLOYMENT_GUIDE.md)
- Logs nos terminais
- Botão "Testar Conexão BD" na aplicação

---

**Desenvolvido com ❤️ para otimizar a gestão de materiais**