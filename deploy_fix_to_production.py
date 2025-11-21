#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Deploy Seguro - Aplicar Correções de Homologação para Produção
Este script aplica as correções do endpoint /api/consulta_material de forma segura.
"""

import os
import shutil
import subprocess
import time
from datetime import datetime

def create_backup():
    """Cria backup do arquivo de produção"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f"fdbacc.py.backup.{timestamp}"
    
    try:
        shutil.copy2('fdbacc.py', backup_name)
        print(f"✅ Backup criado: {backup_name}")
        return backup_name
    except Exception as e:
        print(f"❌ Erro ao criar backup: {e}")
        return None

def check_production_service():
    """Verifica se o serviço de produção está rodando"""
    try:
        import requests
        import urllib3
        urllib3.disable_warnings()
        
        response = requests.get('https://localhost:5000/health', verify=False, timeout=5)
        if response.status_code == 200:
            print("✅ Serviço de produção está rodando")
            return True
        else:
            print(f"⚠️ Serviço de produção retornou status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao verificar serviço de produção: {e}")
        return False

def apply_fix():
    """Aplica a correção no arquivo de produção"""
    try:
        # Ler o arquivo atual
        with open('fdbacc.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar se a correção já foi aplicada
        if 'len(result) > 4 and result[4] is not None' in content:
            print("✅ Correção já aplicada no arquivo de produção")
            return True
        
        # Aplicar a correção - substituir a lógica de formatação das quantidades
        old_pattern = """                # Adiciona verificação para evitar erro de NoneType com round()
                qt_etiq_formatada = round(resultado_sp[4], 2) if resultado_sp[4] is not None else None
                qt_rec_formatada = round(resultado_sp[5], 2) if resultado_sp[5] is not None else None"""
        
        new_pattern = """                # Adiciona verificação para evitar erro de NoneType com round()
                # Correção aplicada: verificação adicional de índice para compatibilidade
                qt_etiq_formatada = round(resultado_sp[4], 2) if len(resultado_sp) > 4 and resultado_sp[4] is not None else None
                qt_rec_formatada = round(resultado_sp[5], 2) if len(resultado_sp) > 5 and resultado_sp[5] is not None else None"""
        
        if old_pattern in content:
            content = content.replace(old_pattern, new_pattern)
            
            # Escrever o arquivo modificado
            with open('fdbacc.py', 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ Correção aplicada com sucesso")
            return True
        else:
            print("⚠️ Padrão não encontrado - arquivo pode já estar corrigido ou ter estrutura diferente")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao aplicar correção: {e}")
        return False

def test_endpoint():
    """Testa o endpoint após aplicar a correção"""
    try:
        import requests
        import json
        import urllib3
        urllib3.disable_warnings()
        
        print("🧪 Testando endpoint de produção...")
        
        response = requests.post(
            'https://localhost:5000/api/consulta_material',
            json={'codigo': 'AA148355'},
            verify=False,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            required_fields = ['codigomoldes', 'descricao', 'tipo', 'proced', 'qt_etiq', 'qt_rec']
            
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields:
                print("✅ Endpoint funcionando corretamente - todos os campos presentes")
                return True
            else:
                print(f"❌ Campos ausentes: {missing_fields}")
                return False
        else:
            print(f"❌ Endpoint retornou status: {response.status_code}")
            print(f"Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar endpoint: {e}")
        return False

def rollback(backup_file):
    """Faz rollback para o backup em caso de problemas"""
    try:
        if os.path.exists(backup_file):
            shutil.copy2(backup_file, 'fdbacc.py')
            print(f"✅ Rollback realizado com sucesso usando: {backup_file}")
            return True
        else:
            print(f"❌ Arquivo de backup não encontrado: {backup_file}")
            return False
    except Exception as e:
        print(f"❌ Erro ao fazer rollback: {e}")
        return False

def main():
    """Função principal do deploy"""
    print("="*60)
    print("🚀 DEPLOY SEGURO - CORREÇÃO CONSULTA MATERIAL")
    print("="*60)
    
    # Verificar se estamos no diretório correto
    if not os.path.exists('fdbacc.py'):
        print("❌ Arquivo fdbacc.py não encontrado no diretório atual")
        return False
    
    # Passo 1: Criar backup
    print("\n📦 Passo 1: Criando backup...")
    backup_file = create_backup()
    if not backup_file:
        print("❌ Deploy cancelado - falha ao criar backup")
        return False
    
    # Passo 2: Verificar serviço
    print("\n🔍 Passo 2: Verificando serviço de produção...")
    if not check_production_service():
        print("⚠️ Serviço de produção não está respondendo - continuando mesmo assim")
    
    # Passo 3: Aplicar correção
    print("\n🔧 Passo 3: Aplicando correção...")
    if not apply_fix():
        print("❌ Deploy cancelado - falha ao aplicar correção")
        return False
    
    # Passo 4: Aguardar reinicialização automática
    print("\n⏳ Passo 4: Aguardando reinicialização do serviço...")
    time.sleep(5)
    
    # Passo 5: Testar endpoint
    print("\n🧪 Passo 5: Testando endpoint...")
    if test_endpoint():
        print("\n🎉 DEPLOY REALIZADO COM SUCESSO!")
        print(f"📁 Backup disponível em: {backup_file}")
        return True
    else:
        print("\n❌ Teste falhou - iniciando rollback...")
        if rollback(backup_file):
            print("✅ Rollback concluído")
        else:
            print("❌ Falha no rollback - intervenção manual necessária")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Deploy concluído com sucesso!")
    else:
        print("\n❌ Deploy falhou - verifique os logs acima")