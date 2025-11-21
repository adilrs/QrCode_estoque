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

def verificar_tabela_moldes():
    """Verifica a estrutura da tabela moldes"""
    try:
        with fdb.connect(
            database=DB_PATH,
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            charset=DB_ENCODING
        ) as con:
            cur = con.cursor()
            
            # Query para verificar colunas da tabela moldes
            query = """
                SELECT 
                    rf.RDB$FIELD_NAME as field_name,
                    f.RDB$FIELD_TYPE as field_type,
                    f.RDB$FIELD_LENGTH as field_length
                FROM RDB$RELATION_FIELDS rf
                JOIN RDB$FIELDS f ON rf.RDB$FIELD_SOURCE = f.RDB$FIELD_NAME
                WHERE rf.RDB$RELATION_NAME = 'MOLDES'
                ORDER BY rf.RDB$FIELD_POSITION
            """
            
            cur.execute(query)
            campos = cur.fetchall()
            
            if campos:
                print("\n=== ESTRUTURA DA TABELA MOLDES ===")
                for campo in campos:
                    nome_campo = campo[0].strip() if campo[0] else 'N/A'
                    tipo_campo = campo[1] if campo[1] else 'N/A'
                    tamanho_campo = campo[2] if campo[2] else 'N/A'
                    print(f"  {nome_campo} - Tipo: {tipo_campo}, Tamanho: {tamanho_campo}")
                    
                # Verificar se existe o campo LOCALIZACAO
                campos_nomes = [campo[0].strip().upper() for campo in campos]
                if 'LOCALIZACAO' in campos_nomes:
                    print("\n✅ Campo LOCALIZACAO encontrado na tabela MOLDES")
                else:
                    print("\n❌ Campo LOCALIZACAO NÃO encontrado na tabela MOLDES")
                    
            else:
                print("\nTabela MOLDES não encontrada ou sem campos")
                
            # Testar uma consulta simples na tabela moldes
            print("\n=== TESTE DE CONSULTA NA TABELA MOLDES ===")
            try:
                test_query = "SELECT FIRST 5 codigomoldes, DESCRICAODOMOLDE FROM moldes"
                cur.execute(test_query)
                resultados = cur.fetchall()
                print(f"Encontrados {len(resultados)} registros na tabela moldes")
                for row in resultados:
                    print(f"  Código: {row[0]}, Descrição: {row[1]}")
            except Exception as e:
                print(f"Erro ao consultar tabela moldes: {e}")
                
            # Testar consulta com campo localizacao
            print("\n=== TESTE DE CONSULTA COM CAMPO LOCALIZACAO ===")
            try:
                loc_query = "SELECT FIRST 5 codigomoldes, DESCRICAODOMOLDE, localizacao FROM moldes WHERE localizacao IS NOT NULL"
                cur.execute(loc_query)
                resultados = cur.fetchall()
                print(f"Encontrados {len(resultados)} registros com localização preenchida")
                for row in resultados:
                    print(f"  Código: {row[0]}, Descrição: {row[1]}, Localização: {row[2]}")
            except Exception as e:
                print(f"Erro ao consultar campo localizacao: {e}")
                
    except Exception as e:
        print(f"Erro ao verificar tabela moldes: {e}")

if __name__ == '__main__':
    print("Verificando estrutura da tabela MOLDES...")
    verificar_tabela_moldes()
    print("\n=== VERIFICAÇÃO CONCLUÍDA ===")