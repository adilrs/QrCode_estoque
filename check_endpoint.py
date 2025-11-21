#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar se o endpoint está presente no arquivo
"""

import os

print("=== Verificando arquivo fdbacc.py ===")

# Verificar se o arquivo existe
if os.path.exists('fdbacc.py'):
    print("✅ Arquivo fdbacc.py existe")
    
    # Ler o conteúdo do arquivo
    with open('fdbacc.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar se o endpoint está presente
    if '/api/requisicoes_pendentes' in content:
        print("✅ Endpoint /api/requisicoes_pendentes encontrado no arquivo")
    else:
        print("❌ Endpoint /api/requisicoes_pendentes NÃO encontrado no arquivo")
    
    # Verificar se a função está presente
    if 'def requisicoes_pendentes():' in content:
        print("✅ Função requisicoes_pendentes() encontrada no arquivo")
    else:
        print("❌ Função requisicoes_pendentes() NÃO encontrada no arquivo")
    
    # Contar linhas
    lines = content.split('\n')
    print(f"📊 Total de linhas no arquivo: {len(lines)}")
    
    # Verificar timestamp
    timestamp = os.path.getmtime('fdbacc.py')
    print(f"📅 Última modificação: {timestamp}")
    
else:
    print("❌ Arquivo fdbacc.py NÃO existe")

print("\n=== Verificando backup ===")
if os.path.exists('fdbacc.py.backup.20250901_154551'):
    backup_timestamp = os.path.getmtime('fdbacc.py.backup.20250901_154551')
    print(f"📅 Backup timestamp: {backup_timestamp}")
else:
    print("❌ Backup não encontrado")