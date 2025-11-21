import requests
import json
import urllib3

# Desabilitar avisos SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def debug_api_response(codigo):
    url = "https://127.0.0.1:5000/api/consulta_material"
    headers = {"Content-Type": "application/json"}
    data = {"codigo": codigo}
    
    print(f"\n=== DEBUG API PARA CÓDIGO: {codigo} ===")
    print(f"URL: {url}")
    print(f"Headers: {headers}")
    print(f"Payload: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.post(url, json=data, headers=headers, verify=False, timeout=10)
        
        print(f"\n--- RESPOSTA HTTP ---")
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        print(f"\n--- CONTEÚDO DA RESPOSTA ---")
        print(f"Texto bruto: {response.text}")
        
        try:
            json_data = response.json()
            print(f"\n--- JSON PARSEADO ---")
            print(json.dumps(json_data, indent=2, ensure_ascii=False))
            
            # Verificar se todos os campos esperados pelo frontend estão presentes
            print(f"\n--- VERIFICAÇÃO DE CAMPOS ---")
            expected_fields = ['codigomoldes', 'descricao', 'qt_etiq', 'qt_rec', 'unidade', 'nreq', 'dep_destino', 'tipo', 'proced', 'localizacao', 'mensagem', 'dep_origem']
            
            for field in expected_fields:
                if field in json_data:
                    print(f"✅ {field}: {json_data[field]}")
                else:
                    print(f"❌ {field}: AUSENTE")
                    
            # Verificar se há campos extras
            extra_fields = set(json_data.keys()) - set(expected_fields)
            if extra_fields:
                print(f"\n--- CAMPOS EXTRAS ---")
                for field in extra_fields:
                    print(f"➕ {field}: {json_data[field]}")
                    
        except json.JSONDecodeError as e:
            print(f"❌ ERRO AO PARSEAR JSON: {e}")
            print(f"Conteúdo não é JSON válido")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ ERRO DE REQUISIÇÃO: {e}")
    except Exception as e:
        print(f"❌ ERRO INESPERADO: {e}")

def test_frontend_mapping(codigo):
    """Simula o mapeamento que o frontend faz dos dados"""
    url = "https://127.0.0.1:5000/api/consulta_material"
    headers = {"Content-Type": "application/json"}
    data = {"codigo": codigo}
    
    try:
        response = requests.post(url, json=data, headers=headers, verify=False, timeout=10)
        
        if response.ok:
            data = response.json()
            
            print(f"\n=== SIMULAÇÃO DO MAPEAMENTO FRONTEND ===")
            
            # Mapear exatamente como o frontend faz
            materialFormatted = {
                'codigo': data.get('codigomoldes'),
                'descricao': data.get('descricao'),
                'quantidade': data.get('qt_etiq'),
                'quantidadeRecebida': data.get('qt_rec'),
                'unidade': data.get('unidade'),
                'valor': 'N/A',
                'valorTotal': 'N/A',
                'requisicao': data.get('nreq'),
                'status': 'ja Baixada' in str(data.get('mensagem', '')) if data.get('mensagem') else ('Pendente' if data.get('qt_rec', 0) > 0 else 'Disponível'),
                'solicitante': data.get('dep_destino'),
                'tipo': data.get('tipo'),
                'procedencia': data.get('proced'),
                'localizacao': data.get('localizacao'),
                'mensagem': data.get('mensagem'),
                'depOrigem': data.get('dep_origem'),
                'depDestino': data.get('dep_destino')
            }
            
            print("Material formatado para o frontend:")
            print(json.dumps(materialFormatted, indent=2, ensure_ascii=False))
            
            # Verificar se há valores None que podem causar problemas
            print(f"\n--- VERIFICAÇÃO DE VALORES NONE ---")
            for key, value in materialFormatted.items():
                if value is None:
                    print(f"⚠️  {key}: None (pode causar problemas no frontend)")
                elif value == '':
                    print(f"⚠️  {key}: String vazia")
                else:
                    print(f"✅ {key}: {value}")
                    
        else:
            print(f"❌ Erro HTTP {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro na simulação: {e}")

if __name__ == "__main__":
    codigo = "AA162042"
    
    # Debug completo da API
    debug_api_response(codigo)
    
    # Teste do mapeamento frontend
    test_frontend_mapping(codigo)