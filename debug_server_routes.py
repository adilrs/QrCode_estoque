#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, '.')

# Importa o módulo fdbacc diretamente
import fdbacc

print("=== DEBUG: Verificando rotas carregadas ===")
print(f"Flask app: {fdbacc.app}")
print(f"Número de rotas: {len(list(fdbacc.app.url_map.iter_rules()))}")

print("\nRotas registradas:")
for rule in fdbacc.app.url_map.iter_rules():
    print(f"  {rule.rule} -> {rule.endpoint} [{', '.join(rule.methods)}]")

print("\n=== Testando rotas individualmente ===")

# Testa cada rota usando o test_client do Flask
with fdbacc.app.test_client() as client:
    routes_to_test = [
        ('/health', 'GET'),
        ('/api/test_db', 'GET'),
        ('/api/requisicoes_pendentes', 'GET')
    ]
    
    for route, method in routes_to_test:
        try:
            if method == 'GET':
                response = client.get(route)
            elif method == 'POST':
                response = client.post(route, json={})
            
            print(f"\n{method} {route}:")
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                print(f"  ✓ Sucesso")
            else:
                print(f"  ✗ Erro: {response.status_code}")
                print(f"  Resposta: {response.get_data(as_text=True)[:100]}...")
                
        except Exception as e:
            print(f"\n{method} {route}:")
            print(f"  ✗ Exceção: {e}")

print("\n=== Debug concluído ===")