# Configuração de Certificados SSL para Celulares Corporativos

## Problema Identificado

O sistema está configurado para usar HTTPS com certificados auto-assinados. Embora o backend esteja funcionando corretamente e os certificados incluam o IP da rede (192.168.2.96), os celulares corporativos não confiam em certificados auto-assinados por padrão, resultando em erros de "failed to fetch".

## Solução Implementada

### 1. Certificados SSL Atualizados

Os certificados SSL foram regenerados para incluir:
- `localhost` (DNS)
- `127.0.0.1` (IP local)
- `192.168.0.95` (IP original)
- `192.168.2.96` (IP atual da rede)

### 2. Arquivos de Certificado

- **cert.pem**: Certificado público
- **key.pem**: Chave privada
- **generate_ssl.py**: Script para regenerar certificados

### 3. Configuração do Backend

O backend Flask está configurado para:
- Usar HTTPS exclusivamente
- Escutar em todas as interfaces (0.0.0.0:5000)
- Aceitar conexões de `https://127.0.0.1:5000` e `https://192.168.2.96:5000`

## Instalação dos Certificados nos Celulares

### Para Android Corporativo:

1. **Copiar o certificado para o celular**:
   - Transfira o arquivo `cert.pem` para o celular via email, USB ou compartilhamento de rede

2. **Instalar o certificado**:
   - Vá em **Configurações** > **Segurança** > **Criptografia e credenciais**
   - Selecione **Instalar um certificado** > **Certificado CA**
   - Navegue até o arquivo `cert.pem` e selecione-o
   - Dê um nome ao certificado (ex: "Sistema Transferência")
   - Confirme a instalação

3. **Verificar a instalação**:
   - Vá em **Configurações** > **Segurança** > **Certificados confiáveis**
   - Verifique se o certificado aparece na lista de "Usuário"

### Para iOS Corporativo:

1. **Copiar o certificado para o iPhone**:
   - Envie o arquivo `cert.pem` por email e abra no iPhone
   - Ou use AirDrop se disponível

2. **Instalar o perfil**:
   - Toque no arquivo anexado no email
   - Vá em **Configurações** > **Geral** > **Perfis**
   - Toque no perfil do certificado e em **Instalar**

3. **Confiar no certificado**:
   - Vá em **Configurações** > **Geral** > **Sobre** > **Configurações de Confiança do Certificado**
   - Ative a chave para o certificado instalado

## URLs de Acesso

- **Frontend**: `http://192.168.2.96:5173`
- **Backend**: `https://192.168.2.96:5000`
- **API Requisições**: `https://192.168.2.96:5000/api/requisicoes_pendentes`

## Teste de Conectividade

Após instalar o certificado, teste o acesso:

1. Abra o navegador do celular
2. Acesse `https://192.168.2.96:5000/api/requisicoes_pendentes`
3. Deve retornar dados JSON sem erros de certificado

## Troubleshooting

### Se ainda houver problemas:

1. **Verificar se o certificado foi instalado corretamente**
2. **Reiniciar o navegador do celular**
3. **Verificar se a rede permite acesso à porta 5000**
4. **Confirmar que o backend está rodando com SSL**

### Comandos para verificar o backend:

```bash
# Verificar se o backend está rodando
netstat -an | findstr :5000

# Testar conectividade local
curl -k https://localhost:5000/api/requisicoes_pendentes
```

## Regeneração de Certificados

Se necessário regenerar os certificados:

```bash
# No diretório do projeto
python generate_ssl.py

# Reiniciar o backend
python fdbacc.py
```

## Notas Importantes

- Os certificados auto-assinados são adequados para ambiente de desenvolvimento/corporativo interno
- Para produção, considere usar certificados de uma CA confiável
- Mantenha os arquivos `cert.pem` e `key.pem` seguros
- Os certificados têm validade de 365 dias a partir da geração