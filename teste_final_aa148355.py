#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste Final - Verificação da Etiqueta AA148355
Este script verifica se o problema foi resolvido após a configuração do proxy
"""

import requests
import json
from urllib3.exceptions import InsecureRequestWarning

# Suprimir avisos de SSL
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def testar_backend_direto():
    """Testa o backend diretamente"""
    print("\n🔧 TESTANDO BACKEND DIRETO (porta 5001)")
    print("=" * 60)
    
    try:
        url = "https://localhost:5001/api/consulta_material"
        data = {"codigo": "AA148355"}
        
        response = requests.post(
            url, 
            json=data, 
            verify=False, 
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Backend funcionando!")
            print(f"Material: {result.get('descricao', 'N/A')}")
            print(f"Quantidade: {result.get('qt_etiq', 'N/A')}")
            print(f"Requisição: {result.get('nreq', 'N/A')}")
            return True
        else:
            print(f"❌ Erro no backend: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro de conexão com backend: {e}")
        return False

def testar_frontend_proxy():
    """Testa o frontend via proxy"""
    print("\n🌐 TESTANDO FRONTEND VIA PROXY (porta 5176)")
    print("=" * 60)
    
    try:
        # Primeiro, verificar se o frontend está acessível
        frontend_url = "https://192.168.2.96:5176"
        response = requests.get(frontend_url, verify=False, timeout=5)
        
        if response.status_code == 200:
            print("✅ Frontend acessível")
        else:
            print(f"⚠️ Frontend com problemas: {response.status_code}")
            
        # Agora testar o proxy
        proxy_url = "https://192.168.2.96:5176/api/consulta_material"
        data = {"codigo": "AA148355"}
        
        response = requests.post(
            proxy_url, 
            json=data, 
            verify=False, 
            timeout=10
        )
        
        print(f"Status Code do Proxy: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Proxy funcionando!")
            print(f"Material via proxy: {result.get('descricao', 'N/A')}")
            print(f"Quantidade via proxy: {result.get('qt_etiq', 'N/A')}")
            print(f"Requisição via proxy: {result.get('nreq', 'N/A')}")
            return True
        else:
            print(f"❌ Erro no proxy: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro de conexão com frontend/proxy: {e}")
        return False

def main():
    print("🧪 TESTE FINAL - ETIQUETA AA148355")
    print("=" * 60)
    print("Verificando se o problema foi resolvido após configuração do proxy...")
    
    # Teste 1: Backend direto
    backend_ok = testar_backend_direto()
    
    # Teste 2: Frontend via proxy
    proxy_ok = testar_frontend_proxy()
    
    # Resultado final
    print("\n📊 RESULTADO FINAL")
    print("=" * 60)
    
    if backend_ok and proxy_ok:
        print("🎉 PROBLEMA RESOLVIDO!")
        print("✅ Backend funcionando")
        print("✅ Proxy configurado corretamente")
        print("✅ Etiqueta AA148355 deve funcionar no frontend agora")
        print("\n💡 SOLUÇÃO APLICADA:")
        print("   - Configurado proxy no vite.config.js")
        print("   - Requisições /api agora são redirecionadas para https://localhost:5001")
        print("   - Certificados auto-assinados aceitos (secure: false)")
        return True
    elif backend_ok and not proxy_ok:
        print("⚠️ PROBLEMA PARCIALMENTE RESOLVIDO")
        print("✅ Backend funcionando")
        print("❌ Proxy ainda com problemas")
        print("\n🔧 PRÓXIMOS PASSOS:")
        print("   - Verificar se o servidor frontend reiniciou corretamente")
        print("   - Verificar logs do Vite para erros de proxy")
        return False
    elif not backend_ok and proxy_ok:
        print("⚠️ PROBLEMA NO BACKEND")
        print("❌ Backend com problemas")
        print("✅ Proxy funcionando")
        return False
    else:
        print("❌ PROBLEMA PERSISTE")
        print("❌ Backend com problemas")
        print("❌ Proxy com problemas")
        return False

if __name__ == "__main__":
    main()