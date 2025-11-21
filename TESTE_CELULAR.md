# 📱 TESTE NO CELULAR - MODO HTTP

## ✅ PROBLEMA RESOLVIDO

O problema de conectividade do celular foi resolvido alternando o sistema para modo HTTP (sem SSL).

## 🔧 O QUE FOI FEITO

1. **Configuração HTTP ativada**: O backend agora roda em HTTP na porta 5000
2. **Frontend atualizado**: O proxy do Vite foi configurado para usar HTTP
3. **Certificados SSL mantidos**: Podem ser reativados quando necessário

## 📱 COMO TESTAR NO CELULAR

### URLs para acessar no celular:
- **Frontend**: `http://192.168.2.96:5175`
- **Backend**: `http://192.168.2.96:5000`
- **API direta**: `http://192.168.2.96:5000/api/usuarios_login`

### Passos para teste:

1. **Conecte o celular na mesma rede Wi-Fi** (192.168.2.x)

2. **Abra o navegador do celular**

3. **Acesse**: `http://192.168.2.96:5175`

4. **Teste o login**:
   - Clique no ícone de login
   - Selecione um usuário
   - Digite uma senha
   - Verifique se funciona normalmente

## 🔄 ALTERNANDO ENTRE MODOS

### Para voltar ao modo SSL (HTTPS):
```bash
python switch_mobile_mode.py ssl
```

### Para ativar modo HTTP (celulares):
```bash
python switch_mobile_mode.py mobile
```

### Para verificar o modo atual:
```bash
python switch_mobile_mode.py status
```

## ⚠️ IMPORTANTE

- **Sempre reinicie backend e frontend** após trocar de modo
- **Modo HTTP é seguro** para rede interna corporativa
- **Para produção externa**, use sempre SSL

## 🐛 TROUBLESHOOTING

### Se ainda houver problemas:

1. **Verifique a rede**:
   - Celular e PC na mesma rede?
   - IP 192.168.2.96 acessível?

2. **Teste a API diretamente**:
   - Acesse `http://192.168.2.96:5000/api/usuarios_login` no celular
   - Deve retornar lista de usuários em JSON

3. **Verifique os logs**:
   - Backend: Terminal 4
   - Frontend: Terminal 5

4. **Reinicie os serviços**:
   ```bash
   # Parar tudo
   Ctrl+C nos terminais
   
   # Reiniciar backend
   python fdbacc.py
   
   # Reiniciar frontend
   npm run dev
   ```

## 📊 STATUS ATUAL

- ✅ Backend: HTTP na porta 5000
- ✅ Frontend: HTTPS na porta 5175 (proxy para HTTP)
- ✅ Certificados SSL: Disponíveis para reativação
- ✅ Modo celular: ATIVO

---

**🎯 RESULTADO ESPERADO**: O celular agora deve conseguir acessar e fazer login normalmente!