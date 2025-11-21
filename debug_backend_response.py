import fdb
import os
from dotenv import load_dotenv
import json

# Carregar variáveis de ambiente
load_dotenv('.env')

# Configurações do banco de dados
DB_HOST = os.getenv('DB_HOST', '192.168.0.8')
DB_PATH = os.getenv('DB_PATH', 'e:/gdb/retesp.fdb')
DB_USER = os.getenv('DB_USER', 'SYSDBA')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'a')
DB_ENCODING = os.getenv('DB_ENCODING', 'UTF8')

def debug_backend_response():
    """Debug da formatação da resposta do backend"""
    try:
        with fdb.connect(
            database=DB_PATH,
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            charset=DB_ENCODING
        ) as con:
            cur = con.cursor()
            
            # Query exata do fdbacc.py
            query = """
                SELECT 
                    m.codigomoldes as cod_item, 
                    m.DESCRICAODOMOLDE as material, 
                    a.DATA as dt_requisicao, 
                    a1.ALMOXARIFE as dep_origem,
                    ps.FISICO ,
                    a2.ALMOXARIFE as dep_destino, 
                    v.NREC,
                    v.ETIQ,
                    v.QUANTIDADE as qt_volume,
                    COALESCE(a.QT_ORIGINAL, v.QUANTIDADE) as qt_requisitada , 
                    m.localizacao 
                FROM REQUISICOES_ALMX a 
                INNER JOIN DS_ENTRA_ESTOQUE_VOLS v ON v.NREC = a.NREQ AND v.BAIXADO = 0 
                INNER JOIN MOVIM_ALMOX a1 ON a1.CODIGOALM = a.ALMX_ORIG 
                    inner join PRODUTOS_SALDO ps on ps.codigomoldes = v.codigomoldes and ps.CODIGOALM = a1.CODIGOALM
                INNER JOIN MOVIM_ALMOX a2 ON a2.CODIGOALM = a.ALMX_DEST 
                INNER JOIN moldes m ON m.codigomoldes = a.CODIGOMOLDES 
                WHERE a.data > '1.1.2024'
                ORDER BY a.DATA DESC
            """
            
            print("\n=== DEBUG DA FORMATAÇÃO DO BACKEND ===")
            cur.execute(query)
            resultados = cur.fetchall()
            
            if resultados:
                print(f"Encontradas {len(resultados)} requisições")
                
                # Simular a formatação exata do backend
                requisicoes = []
                for i, row in enumerate(resultados[:3]):
                    print(f"\n=== PROCESSANDO LINHA {i+1} ===")
                    print(f"row[10] original: '{row[10]}' (tipo: {type(row[10])})")
                    print(f"row[10] is None: {row[10] is None}")
                    print(f"bool(row[10]): {bool(row[10]) if row[10] is not None else 'N/A'}")
                    
                    # Formatação exata do fdbacc.py
                    localizacao_formatada = row[10] if row[10] else 'N/A'
                    print(f"Localização formatada: '{localizacao_formatada}'")
                    
                    requisicao = {
                        'cod_item': row[0],
                        'material': row[1],
                        'dt_requisicao': row[2].strftime('%d/%m/%Y') if row[2] else None,
                        'dep_origem': row[3],
                        'saldo': round(float(row[4]), 2) if row[4] is not None else 0,
                        'dep_destino': row[5],
                        'nrec': row[6],
                        'etiq': row[7],
                        'qt_volume': float(row[8]) if row[8] is not None else 0,
                        'qt_requisitada': float(row[9]) if row[9] is not None else 0,
                        'localizacao': row[10] if row[10] else 'N/A'
                    }
                    
                    print(f"Objeto requisição criado:")
                    print(f"  localizacao: '{requisicao['localizacao']}'")
                    
                    requisicoes.append(requisicao)
                
                # Simular resposta JSON
                response_data = {
                    'status': 'success',
                    'total': len(requisicoes),
                    'requisicoes': requisicoes,
                    'environment': 'homologacao'
                }
                
                print(f"\n=== RESPOSTA JSON SIMULADA ===")
                json_response = json.dumps(response_data, indent=2, default=str)
                print(json_response[:1000] + "..." if len(json_response) > 1000 else json_response)
                
                # Verificar especificamente as localizações
                print(f"\n=== VERIFICAÇÃO DAS LOCALIZAÇÕES ===")
                for i, req in enumerate(requisicoes):
                    print(f"Requisição {i+1}: '{req['localizacao']}'")
                    
            else:
                print("Nenhuma requisição encontrada")
                
    except Exception as e:
        print(f"Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    debug_backend_response()