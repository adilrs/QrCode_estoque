#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para alternar entre modo SSL e modo HTTP para celulares
"""

import os
import shutil
import sys

def switch_to_mobile_mode():
    """Alterna para modo HTTP (sem SSL) para celulares"""
    print("🔄 Alternando para modo HTTP (celulares)...")
    
    # Backup do .env atual
    if os.path.exists('.env'):
        shutil.copy('.env', '.env.ssl.backup')
        print("✅ Backup do .env atual criado (.env.ssl.backup)")
    
    # Copiar configuração mobile
    if os.path.exists('.env.mobile'):
        shutil.copy('.env.mobile', '.env')
        print("✅ Configuração mobile ativada")
    else:
        print("❌ Arquivo .env.mobile não encontrado!")
        return False
    
    # Atualizar vite.config.js para HTTP
    update_vite_config_http()
    
    print("\n📱 MODO CELULAR ATIVADO")
    print("URLs de acesso:")
    print("- Backend: http://192.168.2.96:5000")
    print("- Frontend: http://192.168.2.96:5175")
    print("\n⚠️  IMPORTANTE: Reinicie o backend e frontend!")
    return True

def switch_to_ssl_mode():
    """Alterna para modo SSL (HTTPS)"""
    print("🔄 Alternando para modo SSL (HTTPS)...")
    
    # Restaurar backup do .env SSL
    if os.path.exists('.env.ssl.backup'):
        shutil.copy('.env.ssl.backup', '.env')
        print("✅ Configuração SSL restaurada")
    else:
        print("❌ Backup SSL não encontrado (.env.ssl.backup)!")
        return False
    
    # Atualizar vite.config.js para HTTPS
    update_vite_config_https()
    
    print("\n🔒 MODO SSL ATIVADO")
    print("URLs de acesso:")
    print("- Backend: https://192.168.2.96:5000")
    print("- Frontend: https://192.168.2.96:5175")
    print("\n⚠️  IMPORTANTE: Reinicie o backend e frontend!")
    return True

def update_vite_config_http():
    """Atualiza vite.config.js para usar HTTP"""
    try:
        with open('vite.config.js', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Substituir HTTPS por HTTP no proxy
        content = content.replace('https://192.168.2.96:5000', 'http://192.168.2.96:5000')
        
        with open('vite.config.js', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ vite.config.js atualizado para HTTP")
    except Exception as e:
        print(f"❌ Erro ao atualizar vite.config.js: {e}")

def update_vite_config_https():
    """Atualiza vite.config.js para usar HTTPS"""
    try:
        with open('vite.config.js', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Substituir HTTP por HTTPS no proxy
        content = content.replace('http://192.168.2.96:5000', 'https://192.168.2.96:5000')
        
        with open('vite.config.js', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ vite.config.js atualizado para HTTPS")
    except Exception as e:
        print(f"❌ Erro ao atualizar vite.config.js: {e}")

def show_status():
    """Mostra o status atual"""
    print("📊 STATUS ATUAL:")
    
    # Verificar .env
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            content = f.read()
            if 'FORCE_NO_SSL=True' in content:
                print("🔓 Modo: HTTP (celulares)")
            else:
                print("🔒 Modo: SSL (HTTPS)")
    else:
        print("❌ Arquivo .env não encontrado")
    
    # Verificar vite.config.js
    if os.path.exists('vite.config.js'):
        with open('vite.config.js', 'r') as f:
            content = f.read()
            if 'http://192.168.2.96:5000' in content:
                print("📱 Frontend: Configurado para HTTP")
            elif 'https://192.168.2.96:5000' in content:
                print("🔒 Frontend: Configurado para HTTPS")
    else:
        print("❌ Arquivo vite.config.js não encontrado")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("🔧 Script para alternar entre modo SSL e HTTP")
        print("\nUso:")
        print("  python switch_mobile_mode.py mobile   # Ativar modo HTTP para celulares")
        print("  python switch_mobile_mode.py ssl      # Ativar modo SSL (HTTPS)")
        print("  python switch_mobile_mode.py status   # Mostrar status atual")
        sys.exit(1)
    
    mode = sys.argv[1].lower()
    
    if mode == 'mobile':
        switch_to_mobile_mode()
    elif mode == 'ssl':
        switch_to_ssl_mode()
    elif mode == 'status':
        show_status()
    else:
        print("❌ Modo inválido. Use: mobile, ssl ou status")
        sys.exit(1)