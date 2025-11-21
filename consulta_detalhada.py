#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para consulta detalhada da API e análise dos dados
"""

import requests
import urllib3
import json
from datetime import datetime

# Desabilitar avisos de SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def consulta_detalhada_material(codigo):
    base_url = "https://192.168.2.96:5000"
    
    print("=== CONSULTA DETALHADA DE MATERIAL ===")
    print(f"Código: {codigo}")
    print(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 50)
    
    try:
        payload = {"codigo": codigo}
        response = requests.post(
            f"{base_url}/api/consulta_material", 
            json=payload, 
            verify=False, 
            timeout=30
        )
        
        print(f"Status HTTP: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print()
        
        if response.status_code == 200:
            data = response.json()
            
            print("DADOS RETORNADOS PELA API:")
            print("-" * 30)
            
            # Campos principais
            print(f"Código Moldes: {data.get('codigomoldes', 'N/A')}")
            print(f"Descrição: {data.get('descricao', 'N/A')}")
            print(f"Tipo: {data.get('tipo', 'N/A')}")
            print(f"Procedência: {data.get('proced', 'N/A')}")
            print()
            
            # Quantidades
            qt_etiq = data.get('qt_etiq', 0)
            qt_rec = data.get('qt_rec', 0)
            unidade = data.get('unidade', 'N/A')
            
            print("QUANTIDADES:")
            print(f"  Quantidade Etiqueta: {qt_etiq} {unidade}")
            print(f"  Quantidade Recebida: {qt_rec} {unidade}")
            print(f"  Diferença: {qt_etiq - qt_rec if qt_etiq and qt_rec else 'N/A'} {unidade}")
            print()
            
            # Status calculado
            if qt_rec > 0:
                status = "Pendente"
                cor_status = "🟡"
            else:
                status = "Disponível"
                cor_status = "⚪"
            
            print(f"STATUS CALCULADO: {cor_status} {status}")
            print(f"  Lógica: qt_rec ({qt_rec}) > 0 = {'Sim' if qt_rec > 0 else 'Não'}")
            print()
            
            # Localização e departamentos
            print("LOCALIZAÇÃO E DEPARTAMENTOS:")
            print(f"  Localização: {data.get('localizacao', 'N/A')}")
            print(f"  Dep. Origem: {data.get('dep_origem', 'N/A')}")
            print(f"  Dep. Destino: {data.get('dep_destino', 'N/A')}")
            print(f"  Nº Requisição: {data.get('nreq', 'N/A')}")
            print()
            
            # Mensagem
            mensagem = data.get('mensagem', '')
            if mensagem:
                print(f"MENSAGEM: 🔴 {mensagem}")
            else:
                print("MENSAGEM: Nenhuma")
            print()
            
            # Análise para tomada de decisão
            print("ANÁLISE PARA TOMADA DE DECISÃO:")
            print("-" * 35)
            
            if mensagem and "ja Baixada" in mensagem:
                print("✅ Etiqueta já foi baixada do sistema")
                print("✅ Material já foi processado anteriormente")
                
            if qt_rec > 0:
                print(f"⚠️  Material tem quantidade recebida ({qt_rec})")
                print("⚠️  Status: PENDENTE - Aguardando ação")
                
                if qt_rec == qt_etiq:
                    print("✅ Quantidade recebida = Quantidade etiqueta")
                    print("💡 Sugestão: Material pode ser transferido")
                elif qt_rec < qt_etiq:
                    print(f"⚠️  Recebido ({qt_rec}) < Etiqueta ({qt_etiq})")
                    print("💡 Sugestão: Verificar se há mais material a receber")
                else:
                    print(f"🔴 Recebido ({qt_rec}) > Etiqueta ({qt_etiq})")
                    print("💡 Sugestão: Verificar inconsistência nos dados")
            else:
                print("✅ Material disponível para recebimento")
                print("💡 Sugestão: Pode processar nova entrada")
            
            print()
            print("DADOS COMPLETOS (JSON):")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
        else:
            print(f"❌ Erro na consulta: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Detalhes: {error_data}")
            except:
                print(f"Resposta: {response.text}")
                
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
    
    print("\n" + "=" * 50)
    print("CONSULTA FINALIZADA")

if __name__ == "__main__":
    # Consulta o material de teste
    consulta_detalhada_material("AA162026")