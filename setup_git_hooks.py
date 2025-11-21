#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para configurar Git Hooks automatizados
Implementa validação automática de padrões de desenvolvimento
"""

import os
import stat
import subprocess
from pathlib import Path

class GitHooksSetup:
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or os.getcwd())
        self.git_dir = self.project_root / '.git'
        self.hooks_dir = self.git_dir / 'hooks'
        
    def create_pre_commit_hook(self):
        """Cria hook de pre-commit para validação automática"""
        hook_content = '''#!/bin/sh
# Pre-commit hook para validação de padrões de desenvolvimento

echo "🔍 Executando validação de padrões..."

# Executa o validador de padrões
python validate_standards.py --path . --strict

if [ $? -ne 0 ]; then
    echo "❌ Commit bloqueado devido a violações de padrões!"
    echo "💡 Execute 'python validate_standards.py' para ver detalhes"
    exit 1
fi

echo "✅ Padrões validados com sucesso!"
exit 0
'''
        
        hook_file = self.hooks_dir / 'pre-commit'
        
        with open(hook_file, 'w', encoding='utf-8') as f:
            f.write(hook_content)
            
        # Torna o arquivo executável
        hook_file.chmod(hook_file.stat().st_mode | stat.S_IEXEC)
        
        print(f"✅ Hook pre-commit criado: {hook_file}")
        
    def create_pre_push_hook(self):
        """Cria hook de pre-push para validação final"""
        hook_content = '''#!/bin/sh
# Pre-push hook para validação final antes do push

echo "🚀 Executando validação final antes do push..."

# Executa testes se existirem
if [ -f "requirements.txt" ] && grep -q "pytest" requirements.txt; then
    echo "🧪 Executando testes..."
    python -m pytest
    if [ $? -ne 0 ]; then
        echo "❌ Push bloqueado: testes falharam!"
        exit 1
    fi
fi

# Validação de padrões
python validate_standards.py --path . --strict

if [ $? -ne 0 ]; then
    echo "❌ Push bloqueado devido a violações de padrões!"
    exit 1
fi

echo "✅ Validação final concluída com sucesso!"
exit 0
'''
        
        hook_file = self.hooks_dir / 'pre-push'
        
        with open(hook_file, 'w', encoding='utf-8') as f:
            f.write(hook_content)
            
        # Torna o arquivo executável
        hook_file.chmod(hook_file.stat().st_mode | stat.S_IEXEC)
        
        print(f"✅ Hook pre-push criado: {hook_file}")
        
    def create_commit_msg_hook(self):
        """Cria hook para validar mensagens de commit"""
        hook_content = '''#!/bin/sh
# Commit-msg hook para validar formato das mensagens de commit

commit_regex='^(feat|fix|docs|style|refactor|test|chore)(\\(.+\\))?: .{1,50}'

error_msg="❌ Formato de commit inválido!
💡 Use o formato: tipo(escopo): descrição
📝 Tipos válidos: feat, fix, docs, style, refactor, test, chore
📋 Exemplo: feat(api): adicionar endpoint de consulta"

if ! grep -qE "$commit_regex" "$1"; then
    echo "$error_msg" >&2
    exit 1
fi

echo "✅ Mensagem de commit válida!"
exit 0
'''
        
        hook_file = self.hooks_dir / 'commit-msg'
        
        with open(hook_file, 'w', encoding='utf-8') as f:
            f.write(hook_content)
            
        # Torna o arquivo executável
        hook_file.chmod(hook_file.stat().st_mode | stat.S_IEXEC)
        
        print(f"✅ Hook commit-msg criado: {hook_file}")
        
    def setup_all_hooks(self):
        """Configura todos os hooks"""
        if not self.git_dir.exists():
            print("❌ Diretório .git não encontrado. Inicialize o repositório Git primeiro.")
            return False
            
        if not self.hooks_dir.exists():
            self.hooks_dir.mkdir(parents=True)
            
        print("🔧 Configurando Git Hooks...")
        print("="*50)
        
        self.create_pre_commit_hook()
        self.create_pre_push_hook()
        self.create_commit_msg_hook()
        
        print("\n✅ Todos os hooks foram configurados com sucesso!")
        print("\n📋 Hooks ativos:")
        print("   • pre-commit: Valida padrões antes do commit")
        print("   • pre-push: Executa testes e validação final")
        print("   • commit-msg: Valida formato da mensagem")
        
        return True
        
    def remove_hooks(self):
        """Remove todos os hooks configurados"""
        hooks_to_remove = ['pre-commit', 'pre-push', 'commit-msg']
        
        for hook_name in hooks_to_remove:
            hook_file = self.hooks_dir / hook_name
            if hook_file.exists():
                hook_file.unlink()
                print(f"🗑️  Hook removido: {hook_name}")
                
        print("✅ Todos os hooks foram removidos!")
        
    def test_hooks(self):
        """Testa se os hooks estão funcionando"""
        print("🧪 Testando hooks...")
        
        # Testa o validador de padrões
        try:
            result = subprocess.run(['python', 'validate_standards.py', '--path', '.'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Validador de padrões funcionando")
            else:
                print("⚠️  Validador encontrou problemas (normal se houver violações)")
        except Exception as e:
            print(f"❌ Erro ao testar validador: {e}")
            
        # Verifica se os hooks existem e são executáveis
        hooks_to_check = ['pre-commit', 'pre-push', 'commit-msg']
        
        for hook_name in hooks_to_check:
            hook_file = self.hooks_dir / hook_name
            if hook_file.exists() and os.access(hook_file, os.X_OK):
                print(f"✅ Hook {hook_name} configurado e executável")
            else:
                print(f"❌ Hook {hook_name} não encontrado ou não executável")

def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Configurador de Git Hooks')
    parser.add_argument('--setup', action='store_true', help='Configura todos os hooks')
    parser.add_argument('--remove', action='store_true', help='Remove todos os hooks')
    parser.add_argument('--test', action='store_true', help='Testa os hooks')
    parser.add_argument('--path', '-p', default='.', help='Caminho do projeto')
    
    args = parser.parse_args()
    
    setup = GitHooksSetup(args.path)
    
    if args.setup:
        setup.setup_all_hooks()
    elif args.remove:
        setup.remove_hooks()
    elif args.test:
        setup.test_hooks()
    else:
        print("🔧 Configurador de Git Hooks")
        print("\nUso:")
        print("  python setup_git_hooks.py --setup    # Configura hooks")
        print("  python setup_git_hooks.py --remove   # Remove hooks")
        print("  python setup_git_hooks.py --test     # Testa hooks")
        
if __name__ == '__main__':
    main()