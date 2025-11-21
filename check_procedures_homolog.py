#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verifica as stored procedures disponíveis no banco de homologação
"""

import fdb
import os
from dotenv import load_dotenv

# Carregar configurações de homologação
load_dotenv('.env.homologacao')

DB_CONFIG = {
    'host': os.getenv('DB_HOST', '192.168.0.8'),
    'database': os.getenv('DB_PATH', 'e:/gdb/retesp_homolog.fdb'),
    'user': os.getenv('DB_USER', 'SYSDBA'),
    'password': os.getenv('DB_PASSWORD', 'a'),
    'charset': 'UTF8'
}

def check_procedures():
    """Verifica as stored procedures disponíveis"""
    try:
        con = fdb.connect(**DB_CONFIG)
        cursor = con.cursor()
        
        # Consultar stored procedures
        query = """
        SELECT RDB$PROCEDURE_NAME 
        FROM RDB$PROCEDURES 
        WHERE RDB$SYSTEM_FLAG = 0
        ORDER BY RDB$PROCEDURE_NAME
        """
        
        cursor.execute(query)
        procedures = cursor.fetchall()
        
        print("=" * 60)
        print("STORED PROCEDURES DISPONÍVEIS NO BANCO DE HOMOLOGAÇÃO")
        print("=" * 60)
        
        if procedures:
            for proc in procedures:
                proc_name = proc[0].strip()
                print(f"- {proc_name}")
                
                # Verificar se é uma das procedures que precisamos
                if 'BAIXA' in proc_name or 'REQUISICAO' in proc_name or 'MATERIAL' in proc_name:
                    print(f"  ⭐ RELEVANTE: {proc_name}")
        else:
            print("Nenhuma stored procedure encontrada.")
            
        print("\n" + "=" * 60)
        print(f"TOTAL: {len(procedures)} stored procedures")
        print("=" * 60)
        
        con.close()
        
    except Exception as e:
        print(f"Erro ao conectar no banco: {e}")

if __name__ == "__main__":
    check_procedures()