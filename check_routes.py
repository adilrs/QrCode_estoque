#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar as rotas registradas no Flask
"""

import fdbacc

print("=== Rotas Registradas no Flask ===")
for rule in fdbacc.app.url_map.iter_rules():
    print(f"  {rule.rule} -> {rule.endpoint} [{', '.join(rule.methods)}]")

print("\n=== Verificando função requisicoes_pendentes ===")
if 'requisicoes_pendentes' in fdbacc.app.view_functions:
    print("✅ Função 'requisicoes_pendentes' está registrada")
    print(f"Função: {fdbacc.app.view_functions['requisicoes_pendentes']}")
else:
    print("❌ Função 'requisicoes_pendentes' NÃO está registrada")

print("\n=== Todas as funções registradas ===")
for endpoint, func in fdbacc.app.view_functions.items():
    print(f"  {endpoint} -> {func}")