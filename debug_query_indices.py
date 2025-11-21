import fdb
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv('.env')

# Configurações do banco de dados
DB_HOST = os.getenv('DB_HOST', '192.168.0.8')
DB_PATH = os.getenv('DB_PATH', 'e:/gdb/retesp.fdb')
DB_USER = os.getenv('DB_USER', 'SYSDBA')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'a')
DB_ENCODING = os.getenv('DB_ENCODING', 'UTF8')

def debug_query_indices():
    """Debug dos índices da query de requisições pendentes"""
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
            
            print("\n=== DEBUG DOS ÍNDICES DA QUERY ===")
            cur.execute(query)
            resultados = cur.fetchall()
            
            if resultados:
                row = resultados[0]  # Primeira linha
                print(f"\nTotal de colunas retornadas: {len(row)}")
                print("\n=== MAPEAMENTO DOS ÍNDICES ===")
                
                campos = [
                    "cod_item (m.codigomoldes)",
                    "material (m.DESCRICAODOMOLDE)", 
                    "dt_requisicao (a.DATA)",
                    "dep_origem (a1.ALMOXARIFE)",
                    "saldo_fisico (ps.FISICO)",
                    "dep_destino (a2.ALMOXARIFE)",
                    "nrec (v.NREC)",
                    "etiq (v.ETIQ)",
                    "qt_volume (v.QUANTIDADE)",
                    "qt_requisitada (COALESCE)",
                    "localizacao (m.localizacao)"
                ]
                
                for i, (campo, valor) in enumerate(zip(campos, row)):
                    print(f"  Índice {i}: {campo} = '{valor}' (tipo: {type(valor)})")
                    
                print(f"\n=== VERIFICAÇÃO ESPECÍFICA ===")
                print(f"row[10] (localização): '{row[10]}' (tipo: {type(row[10])})")
                print(f"row[4] (saldo físico): '{row[4]}' (tipo: {type(row[4])})")
                
                # Testar formatação como no backend
                localizacao_formatada = row[10] if row[10] else 'N/A'
                print(f"\nLocalização formatada: '{localizacao_formatada}'")
                
            else:
                print("Nenhuma requisição encontrada")
                
    except Exception as e:
        print(f"Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    debug_query_indices()