#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para comparar configurações de rotas entre produção e homologação
"""

import sys
import os

# Adicionar o diretório atual ao path para importar os módulos
sys.path.insert(0, os.getcwd())
sys.path.insert(0, os.path.join(os.getcwd(), 'homologacao'))

def compare_flask_apps():
    """Compara as configurações dos apps Flask de produção e homologação"""
    
    print("=== COMPARAÇÃO DE CONFIGURAÇÕES FLASK ===")
    print("\n1. Importando módulo de PRODUÇÃO...")
    
    try:
        # Importar o módulo de produção
        import fdbacc as prod_app
        print("   ✓ Módulo de produção importado com sucesso")
        
        # Verificar rotas registradas na produção
        print("\n   Rotas registradas na PRODUÇÃO:")
        prod_routes = []
        for rule in prod_app.app.url_map.iter_rules():
            route_info = f"   {rule.rule} -> {rule.endpoint} {list(rule.methods)}"
            print(route_info)
            prod_routes.append((rule.rule, rule.endpoint, list(rule.methods)))
            
    except Exception as e:
        print(f"   ✗ Erro ao importar módulo de produção: {e}")
        prod_routes = []
    
    print("\n2. Importando módulo de HOMOLOGAÇÃO...")
    
    try:
        # Importar o módulo de homologação
        import fdbacc_homolog as homolog_app
        print("   ✓ Módulo de homologação importado com sucesso")
        
        # Verificar rotas registradas na homologação
        print("\n   Rotas registradas na HOMOLOGAÇÃO:")
        homolog_routes = []
        for rule in homolog_app.app.url_map.iter_rules():
            route_info = f"   {rule.rule} -> {rule.endpoint} {list(rule.methods)}"
            print(route_info)
            homolog_routes.append((rule.rule, rule.endpoint, list(rule.methods)))
            
    except Exception as e:
        print(f"   ✗ Erro ao importar módulo de homologação: {e}")
        homolog_routes = []
    
    # Comparar as rotas
    print("\n=== ANÁLISE COMPARATIVA ===")
    
    if prod_routes and homolog_routes:
        # Rotas apenas na produção
        prod_only = [r for r in prod_routes if r not in homolog_routes]
        if prod_only:
            print("\n🔴 Rotas APENAS na PRODUÇÃO:")
            for route in prod_only:
                print(f"   {route[0]} -> {route[1]} {route[2]}")
        
        # Rotas apenas na homologação
        homolog_only = [r for r in homolog_routes if r not in prod_routes]
        if homolog_only:
            print("\n🟡 Rotas APENAS na HOMOLOGAÇÃO:")
            for route in homolog_only:
                print(f"   {route[0]} -> {route[1]} {route[2]}")
        
        # Rotas comuns
        common_routes = [r for r in prod_routes if r in homolog_routes]
        if common_routes:
            print("\n🟢 Rotas COMUNS:")
            for route in common_routes:
                print(f"   {route[0]} -> {route[1]} {route[2]}")
        
        # Verificar especificamente a rota problemática
        print("\n=== VERIFICAÇÃO ESPECÍFICA: /api/requisicoes_pendentes ===")
        
        prod_req_route = [r for r in prod_routes if '/api/requisicoes_pendentes' in r[0]]
        homolog_req_route = [r for r in homolog_routes if '/api/requisicoes_pendentes' in r[0]]
        
        if prod_req_route:
            print(f"   ✓ PRODUÇÃO: {prod_req_route[0]}")
        else:
            print("   ✗ PRODUÇÃO: Rota /api/requisicoes_pendentes NÃO encontrada")
            
        if homolog_req_route:
            print(f"   ✓ HOMOLOGAÇÃO: {homolog_req_route[0]}")
        else:
            print("   ✗ HOMOLOGAÇÃO: Rota /api/requisicoes_pendentes NÃO encontrada")
            
    else:
        print("   ⚠️  Não foi possível comparar as rotas devido a erros de importação")
    
    print("\n=== VERIFICAÇÃO DE CONFIGURAÇÕES ADICIONAIS ===")
    
    # Verificar configurações do Flask
    try:
        print("\n📋 Configurações PRODUÇÃO:")
        print(f"   Debug: {getattr(prod_app.app, 'debug', 'N/A')}")
        print(f"   Testing: {getattr(prod_app.app, 'testing', 'N/A')}")
        print(f"   Secret Key definida: {'Sim' if getattr(prod_app.app, 'secret_key', None) else 'Não'}")
    except:
        print("   ⚠️  Erro ao verificar configurações de produção")
    
    try:
        print("\n📋 Configurações HOMOLOGAÇÃO:")
        print(f"   Debug: {getattr(homolog_app.app, 'debug', 'N/A')}")
        print(f"   Testing: {getattr(homolog_app.app, 'testing', 'N/A')}")
        print(f"   Secret Key definida: {'Sim' if getattr(homolog_app.app, 'secret_key', None) else 'Não'}")
    except:
        print("   ⚠️  Erro ao verificar configurações de homologação")

def test_route_registration():
    """Testa se as rotas estão sendo registradas corretamente"""
    
    print("\n=== TESTE DE REGISTRO DE ROTAS ===")
    
    try:
        # Testar importação direta do módulo de produção
        print("\n🔍 Testando importação direta do módulo de produção...")
        
        # Limpar cache de módulos para garantir importação limpa
        if 'fdbacc' in sys.modules:
            del sys.modules['fdbacc']
            
        import fdbacc
        
        print("   ✓ Módulo importado com sucesso")
        print(f"   ✓ App Flask criado: {type(fdbacc.app)}")
        print(f"   ✓ Número total de rotas: {len(list(fdbacc.app.url_map.iter_rules()))}")
        
        # Verificar se a função requisicoes_pendentes existe
        if hasattr(fdbacc, 'requisicoes_pendentes'):
            print("   ✓ Função 'requisicoes_pendentes' encontrada")
            print(f"   ✓ Tipo da função: {type(fdbacc.requisicoes_pendentes)}")
        else:
            print("   ✗ Função 'requisicoes_pendentes' NÃO encontrada")
            
        # Listar todas as funções disponíveis
        print("\n📋 Funções disponíveis no módulo:")
        functions = [name for name in dir(fdbacc) if callable(getattr(fdbacc, name)) and not name.startswith('_')]
        for func in functions:
            print(f"   - {func}")
            
    except Exception as e:
        print(f"   ✗ Erro durante teste: {e}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")

if __name__ == '__main__':
    print("Iniciando comparação de configurações...\n")
    
    # Executar comparação
    compare_flask_apps()
    
    # Executar teste de registro
    test_route_registration()
    
    print("\n=== COMPARAÇÃO CONCLUÍDA ===")