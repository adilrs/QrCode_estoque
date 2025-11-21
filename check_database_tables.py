#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar as tabelas existentes no banco de dados
e encontrar a tabela correta para requisições.
"""

import fdb
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Configurações do banco de dados
DB_PATH = os.getenv('DB_PATH')
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_ENCODING = os.getenv('DB_ENCODING', 'UTF8')

def listar_tabelas():
    """Lista todas as tabelas do banco de dados"""
    try:
        with fdb.connect(
            database=DB_PATH,
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            charset=DB_ENCODING
        ) as con:
            cur = con.cursor()
            
            # Query para listar todas as tabelas
            query = """
                SELECT RDB$RELATION_NAME
                FROM RDB$RELATIONS
                WHERE RDB$VIEW_BLR IS NULL
                AND (RDB$SYSTEM_FLAG IS NULL OR RDB$SYSTEM_FLAG = 0)
                ORDER BY RDB$RELATION_NAME
            """
            
            cur.execute(query)
            tabelas = cur.fetchall()
            
            print("=== TABELAS ENCONTRADAS NO BANCO ===")
            tabelas_list = []
            for tabela in tabelas:
                nome_tabela = tabela[0].strip()
                tabelas_list.append(nome_tabela)
                print(f"  {nome_tabela}")
            
            print(f"\nTotal de tabelas: {len(tabelas_list)}")
            
            # Procurar tabelas relacionadas a requisições
            print("\n=== TABELAS RELACIONADAS A REQUISIÇÕES ===")
            requisicoes_tables = [t for t in tabelas_list if 'REQUIS' in t.upper()]
            if requisicoes_tables:
                for tabela in requisicoes_tables:
                    print(f"  {tabela}")
            else:
                print("  Nenhuma tabela com 'REQUIS' encontrada")
            
            # Procurar outras possíveis tabelas
            print("\n=== OUTRAS TABELAS POSSIVELMENTE RELACIONADAS ===")
            outras_keywords = ['PEDIDO', 'SOLICIT', 'TRANSF', 'MOVIMENT']
            for keyword in outras_keywords:
                tables_found = [t for t in tabelas_list if keyword in t.upper()]
                if tables_found:
                    print(f"  Tabelas com '{keyword}':")
                    for tabela in tables_found:
                        print(f"    {tabela}")
            
            return tabelas_list
            
    except Exception as e:
        print(f"Erro ao conectar ao banco: {e}")
        return []

def verificar_estrutura_tabela(nome_tabela):
    """Verifica a estrutura de uma tabela específica"""
    try:
        with fdb.connect(
            database=DB_PATH,
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            charset=DB_ENCODING
        ) as con:
            cur = con.cursor()
            
            # Query para verificar colunas da tabela
            query = """
                SELECT 
                    rf.RDB$FIELD_NAME as field_name,
                    f.RDB$FIELD_TYPE as field_type,
                    f.RDB$FIELD_LENGTH as field_length
                FROM RDB$RELATION_FIELDS rf
                JOIN RDB$FIELDS f ON rf.RDB$FIELD_SOURCE = f.RDB$FIELD_NAME
                WHERE rf.RDB$RELATION_NAME = ?
                ORDER BY rf.RDB$FIELD_POSITION
            """
            
            cur.execute(query, (nome_tabela,))
            campos = cur.fetchall()
            
            if campos:
                print(f"\n=== ESTRUTURA DA TABELA {nome_tabela} ===")
                for campo in campos:
                    nome_campo = campo[0].strip() if campo[0] else 'N/A'
                    tipo_campo = campo[1] if campo[1] else 'N/A'
                    tamanho_campo = campo[2] if campo[2] else 'N/A'
                    print(f"  {nome_campo} - Tipo: {tipo_campo}, Tamanho: {tamanho_campo}")
            else:
                print(f"\nTabela {nome_tabela} não encontrada ou sem campos")
                
    except Exception as e:
        print(f"Erro ao verificar estrutura da tabela {nome_tabela}: {e}")

if __name__ == '__main__':
    print("Verificando tabelas do banco de dados...\n")
    
    # Lista todas as tabelas
    tabelas = listar_tabelas()
    
    # Se encontrou tabelas relacionadas a requisições, verifica a estrutura
    requisicoes_tables = [t for t in tabelas if 'REQUIS' in t.upper()]
    if requisicoes_tables:
        for tabela in requisicoes_tables:
            verificar_estrutura_tabela(tabela)
    
    print("\n=== VERIFICAÇÃO CONCLUÍDA ===")