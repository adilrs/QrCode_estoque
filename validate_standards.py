#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Validação de Padrões de Desenvolvimento
Implementa as diretrizes obrigatórias definidas em .development-standards.json
"""

import os
import re
import json
import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Tuple
from datetime import datetime

class DevelopmentStandardsValidator:
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or os.getcwd())
        self.standards_file = self.project_root / '.development-standards.json'
        self.standards = self._load_standards()
        self.violations = []
        self.warnings = []
        
    def _load_standards(self) -> Dict[str, Any]:
        """Carrega as configurações de padrões do arquivo JSON"""
        try:
            with open(self.standards_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Arquivo de padrões não encontrado: {self.standards_file}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"❌ Erro ao ler arquivo de padrões: {e}")
            sys.exit(1)
    
    def validate_file_encoding(self, file_path: Path) -> bool:
        """Valida se arquivo Python tem encoding UTF-8"""
        if file_path.suffix != '.py':
            return True
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                first_lines = [f.readline().strip() for _ in range(3)]
                
            # Verifica se tem declaração de encoding
            encoding_pattern = r'#.*coding[:=]\s*([-\w.]+)'
            has_encoding = any(re.search(encoding_pattern, line) for line in first_lines)
            
            if not has_encoding:
                self.violations.append({
                    'file': str(file_path),
                    'rule': 'python_encoding',
                    'message': 'Arquivo Python deve ter declaração de encoding UTF-8',
                    'line': 1
                })
                return False
                
        except UnicodeDecodeError:
            self.violations.append({
                'file': str(file_path),
                'rule': 'python_encoding',
                'message': 'Arquivo não está em UTF-8',
                'line': 1
            })
            return False
            
        return True
    
    def validate_no_secrets(self, file_path: Path) -> bool:
        """Verifica se não há senhas ou chaves hardcoded"""
        violations_found = False
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            secret_patterns = [
                r'password\s*=\s*["\'][^"\'\']+["\']',
                r'api_key\s*=\s*["\'][^"\'\']+["\']',
                r'secret\s*=\s*["\'][^"\'\']+["\']',
                r'token\s*=\s*["\'][^"\'\']+["\']',
                r'DB_PASSWORD\s*=\s*["\'][^"\'\']+["\']'
            ]
            
            lines = content.split('\n')
            
            for i, line in enumerate(lines, 1):
                for pattern in secret_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        # Exceção para variáveis de ambiente
                        if 'os.environ' in line or 'getenv' in line:
                            continue
                            
                        self.violations.append({
                            'file': str(file_path),
                            'rule': 'no_secrets_in_code',
                            'message': f'Possível senha/chave hardcoded detectada: {line.strip()}',
                            'line': i
                        })
                        violations_found = True
                        
        except Exception as e:
            self.warnings.append({
                'file': str(file_path),
                'message': f'Erro ao verificar secrets: {e}'
            })
            
        return not violations_found
    
    def validate_no_debug_prints(self, file_path: Path) -> bool:
        """Verifica se não há prints de debug"""
        violations_found = False
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            debug_patterns = [
                r'print\s*\([^)]*debug[^)]*\)',
                r'console\.log\s*\([^)]*debug[^)]*\)',
                r'print\s*\([^)]*DEBUG[^)]*\)'
            ]
            
            lines = content.split('\n')
            
            for i, line in enumerate(lines, 1):
                for pattern in debug_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        self.violations.append({
                            'file': str(file_path),
                            'rule': 'no_debug_prints',
                            'message': f'Print de debug detectado: {line.strip()}',
                            'line': i
                        })
                        violations_found = True
                        
        except Exception as e:
            self.warnings.append({
                'file': str(file_path),
                'message': f'Erro ao verificar debug prints: {e}'
            })
            
        return not violations_found
    
    def validate_sql_injection(self, file_path: Path) -> bool:
        """Verifica possíveis vulnerabilidades de SQL injection"""
        violations_found = False
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Padrões que indicam possível SQL injection
            dangerous_patterns = [
                r'"\s*SELECT\s+.*\+.*"',
                r'\'\s*SELECT\s+.*\+.*\'',
                r'f"\s*SELECT\s+.*{.*}.*"',
                r'f\'\s*SELECT\s+.*{.*}.*\'',
                r'%\s*"\s*SELECT',
                r'%\s*\'\s*SELECT'
            ]
            
            lines = content.split('\n')
            
            for i, line in enumerate(lines, 1):
                for pattern in dangerous_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        self.violations.append({
                            'file': str(file_path),
                            'rule': 'sql_injection_risk',
                            'message': f'Possível vulnerabilidade SQL injection: {line.strip()}',
                            'line': i
                        })
                        violations_found = True
                        
        except Exception as e:
            self.warnings.append({
                'file': str(file_path),
                'message': f'Erro ao verificar SQL injection: {e}'
            })
            
        return not violations_found
    
    def validate_todo_comments(self, file_path: Path) -> bool:
        """Verifica se há comentários TODO (não permitidos em produção)"""
        violations_found = False
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            todo_patterns = [
                r'#\s*TODO',
                r'//\s*TODO',
                r'#\s*FIXME',
                r'//\s*FIXME'
            ]
            
            lines = content.split('\n')
            
            for i, line in enumerate(lines, 1):
                for pattern in todo_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        self.warnings.append({
                            'file': str(file_path),
                            'rule': 'no_todo_comments',
                            'message': f'Comentário TODO/FIXME encontrado: {line.strip()}',
                            'line': i
                        })
                        violations_found = True
                        
        except Exception as e:
            self.warnings.append({
                'file': str(file_path),
                'message': f'Erro ao verificar TODO comments: {e}'
            })
            
        return not violations_found
    
    def validate_homologation_structure(self) -> bool:
        """Valida se a estrutura de homologação está configurada corretamente"""
        violations_found = False
        
        # Verifica se existe o diretório de homologação
        homolog_dir = self.project_root / 'homologacao'
        if not homolog_dir.exists():
            self.violations.append({
                'file': 'project_structure',
                'rule': 'homologation_first',
                'message': 'Diretório de homologação não encontrado: homologacao/',
                'severity': 'critical'
            })
            violations_found = True
        else:
            # Verifica arquivos essenciais de homologação
            required_files = [
                'fdbacc_homolog.py',
                '.env.homologacao',
                'deploy.py'
            ]
            
            for required_file in required_files:
                file_path = homolog_dir / required_file
                if not file_path.exists():
                    self.violations.append({
                        'file': f'homologacao/{required_file}',
                        'rule': 'homologation_first',
                        'message': f'Arquivo essencial de homologação não encontrado: {required_file}',
                        'severity': 'warning'
                    })
                    violations_found = True
        
        # Verifica se existe script de teste de homologação
        test_script = self.project_root / 'test_homolog_service.py'
        if not test_script.exists():
            self.violations.append({
                'file': 'test_homolog_service.py',
                'rule': 'homologation_first',
                'message': 'Script de teste de homologação não encontrado: test_homolog_service.py',
                'severity': 'warning'
            })
            violations_found = True
            
        return not violations_found
    
    def validate_file(self, file_path: Path) -> bool:
        """Valida um arquivo específico"""
        if not file_path.exists() or file_path.is_dir():
            return True
            
        # Ignora arquivos de configuração e dependências
        ignore_patterns = ['.git', '__pycache__', '.venv', 'node_modules', '.env']
        if any(pattern in str(file_path) for pattern in ignore_patterns):
            return True
            
        all_valid = True
        
        # Validações aplicáveis a todos os arquivos
        all_valid &= self.validate_no_secrets(file_path)
        all_valid &= self.validate_no_debug_prints(file_path)
        all_valid &= self.validate_todo_comments(file_path)
        
        # Validações específicas por tipo de arquivo
        if file_path.suffix == '.py':
            all_valid &= self.validate_file_encoding(file_path)
            all_valid &= self.validate_sql_injection(file_path)
            
        return all_valid
    
    def validate_project(self) -> bool:
        """Valida todo o projeto"""
        print(f"🔍 Validando padrões de desenvolvimento...")
        print(f"📁 Projeto: {self.project_root}")
        print(f"📋 Padrões: {self.standards['project']['name']} v{self.standards['project']['governance_version']}")
        print("="*60)
        
        all_valid = True
        files_checked = 0
        
        # Valida estrutura de homologação (regra obrigatória)
        if not self.validate_homologation_structure():
            all_valid = False
        
        # Verifica todos os arquivos do projeto
        for file_path in self.project_root.rglob('*'):
            if file_path.is_file():
                files_checked += 1
                if not self.validate_file(file_path):
                    all_valid = False
                    
        print(f"\n📊 Resumo da Validação:")
        print(f"   Arquivos verificados: {files_checked}")
        print(f"   Violações críticas: {len(self.violations)}")
        print(f"   Avisos: {len(self.warnings)}")
        
        if self.violations:
            print("\n❌ VIOLAÇÕES CRÍTICAS:")
            for violation in self.violations:
                print(f"   {violation['file']}:{violation['line']} - {violation['rule']}")
                print(f"      {violation['message']}")
                
        if self.warnings:
            print("\n⚠️  AVISOS:")
            for warning in self.warnings:
                print(f"   {warning['file']} - {warning.get('rule', 'warning')}")
                print(f"      {warning['message']}")
                
        if all_valid and not self.warnings:
            print("\n✅ Todos os padrões foram atendidos!")
        elif all_valid:
            print("\n✅ Padrões críticos atendidos (com avisos)")
        else:
            print("\n❌ Violações críticas encontradas!")
            
        return all_valid
    
    def generate_report(self, output_file: str = None) -> str:
        """Gera relatório detalhado da validação"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'project': self.standards['project'],
            'summary': {
                'violations': len(self.violations),
                'warnings': len(self.warnings),
                'status': 'PASSED' if not self.violations else 'FAILED'
            },
            'violations': self.violations,
            'warnings': self.warnings
        }
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
                
        return json.dumps(report, indent=2, ensure_ascii=False)

def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Validador de Padrões de Desenvolvimento')
    parser.add_argument('--path', '-p', default='.', help='Caminho do projeto')
    parser.add_argument('--report', '-r', help='Arquivo para salvar relatório JSON')
    parser.add_argument('--strict', '-s', action='store_true', help='Modo estrito (falha com avisos)')
    
    args = parser.parse_args()
    
    validator = DevelopmentStandardsValidator(args.path)
    is_valid = validator.validate_project()
    
    if args.report:
        validator.generate_report(args.report)
        print(f"\n📄 Relatório salvo em: {args.report}")
    
    # Modo estrito considera avisos como falhas
    if args.strict and validator.warnings:
        is_valid = False
        
    sys.exit(0 if is_valid else 1)

if __name__ == '__main__':
    main()