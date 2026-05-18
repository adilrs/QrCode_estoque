#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Transferência de Material - Ambiente de Produção
Versão para uso em produção

Este arquivo contém as configurações para o ambiente de produção.
"""

import fdb
import os
import sys
import logging
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from dotenv import load_dotenv
import json
import traceback
from flask import session  
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity  

# Carregar configurações específicas de produção
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'), override=True)

# Configuração de logging para produção
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'DEBUG')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.getenv('LOG_FILE', 'logs/producao.log')),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Configuração do Flask para produção
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'retesp2000')  # Adição minimalista para sessões

# Configurações mínimas para JWT (adicionadas para resolver o KeyError)
app.config['JWT_SECRET_KEY'] = 'a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2'  # Chave secreta fixa
app.config['JWT_TOKEN_LOCATION'] = ['headers']  # Tokens virão no header (Bearer)
app.config['JWT_HEADER_NAME'] = 'Authorization'  # Padrão
app.config['JWT_HEADER_TYPE'] = 'Bearer'  # Padrão

# Inicializa o JWTManager
jwt = JWTManager(app)

CORS(app, origins="*", supports_credentials=True, expose_headers=["Authorization"], allow_headers=["Authorization", "Content-Type"])

# Configurações do banco de dados
DB_CONFIG = {
    'host': os.getenv('DB_HOST', '192.168.0.8'),
    'database': os.getenv('DB_ALIAS', os.getenv('DB_PATH', r'x:\gdb\retesp.fdb')),
    'user': os.getenv('DB_USER', 'SYSDBA'),
    'password': os.getenv('DB_PASSWORD', 'a'),
    'charset': os.getenv('DB_ENCODING', 'UTF8')
}

# Configurações globais
TEST_MODE = os.getenv('TEST_MODE', 'True').lower() == 'true'
ALLOW_ROLLBACK = os.getenv('ALLOW_ROLLBACK', 'True').lower() == 'true'
AUDIT_ENABLED = os.getenv('AUDIT_ENABLED', 'True').lower() == 'true'

# Variável global para armazenar dados do usuário logado
current_user = {'usuario': None, 'codigo': None}

def clear_current_user():
    """Limpa os dados do usuário logado"""
    global current_user
    current_user['usuario'] = None
    current_user['codigo'] = None
    logger.debug("Dados do usuário logado foram limpos")

def log_audit(action, etiqueta, quantidade, result, user_ip=None):
    """Log de auditoria para homologação"""
    if not AUDIT_ENABLED:
        return
    
    audit_data = {
        'timestamp': datetime.now().isoformat(),
        'environment': 'homologacao',
        'action': action,
        'etiqueta': etiqueta,
        'quantidade': quantidade,
        'result': result,
        'user_ip': user_ip or request.remote_addr if request else 'unknown'
    }
    
    audit_file = os.getenv('AUDIT_LOG_FILE', 'logs/audit_homologacao.log')
    try:
        with open(audit_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(audit_data, ensure_ascii=False) + '\n')
    except Exception as e:
        logger.error(f"Erro ao gravar log de auditoria: {e}")

def get_database_connection():
    """Retorna uma conexão com o banco de dados Firebird."""
    try:
        # Acessa o caminho do banco de dados a partir do dicionário de configuração
        db_path = DB_CONFIG.get('database').replace('/', '\\')  # Corrige separadores para Windows
        dsn = f"{DB_CONFIG.get('host')}:{db_path}"
        if not db_path:
            logger.error("O caminho do banco de dados não foi configurado.")
            raise ValueError("Caminho do banco de dados não encontrado na configuração")

        logger.info(f"Conexão Firebird alvo - host: {DB_CONFIG.get('host')}, database: {db_path}")
        logger.info(f"DSN: {dsn}")
        
        con = fdb.connect(
            dsn=dsn,
            user=DB_CONFIG.get('user', 'SYSDBA'),
            password=DB_CONFIG.get('password', 'masterkey'),
            charset=DB_CONFIG.get('charset', 'WIN1252')
        )
        
        logger.debug("Conexão estabelecida com sucesso")
        return con
    except Exception as e:
        logger.error(f"Erro ao conectar ao banco de dados: {e}")
        raise
# Adicione esta função logo após get_database_connection()
def consultar_material(etiqueta): 
    """Consulta informações do material via stored procedure""" 
    con = None 
    try: 
        con = get_database_connection() 
        cursor = con.cursor() 
        
        logger.debug(f"Executando CONSULTA_QR_MATERIAL para etiqueta: {etiqueta}") 
        cursor.callproc('CONSULTA_QR_MATERIAL', [etiqueta]) 
        result = cursor.fetchall() 
        
        if result: 
            logger.debug(f"Material encontrado: {len(result)} registro(s)") 
            return result[0] 
        else: 
            logger.warning(f"Material não encontrado para etiqueta: {etiqueta}") 
            return None 
        
    except Exception as e: 
        logger.error(f"Erro ao consultar material {etiqueta}: {e}") 
        raise 
    finally: 
        if con: 
            con.close()


def executar_baixa_material(etiqueta, quantidade):
    """Executa a baixa do material via stored procedure"""
    con = None
    try:
        con = get_database_connection()
        cursor = con.cursor()
 
        logger.info(f"INÍCIO: Executando SP_BAIXA_REQUISICAO_MAT - Etiqueta: {etiqueta}, Quantidade: {quantidade}")  # Alterado para info
        
        # Inserção: Setando o usuário dinamicamente da sessão (isolado por terminal)
       #if 'user' in session:
        #usuario = session['user']['nome']  # Ajuste 'nome' para o campo real no seu login
       # codigo_user = session['user']['codigo']  # Ajuste 'codigo' para o campo real no seu login
       # cursor.execute("SELECT SET_USER(?, ?) FROM RDB$DATABASE;", (usuario, codigo_user))
       # else:
       #     raise ValueError("Usuário não logado")
        
        cursor.callproc('SP_BAIXA_REQUISICAO_MAT', [etiqueta])
        result = cursor.fetchone()
        
        if result:
            qtd_retorno = result[0]
            logger.info(f"Resultado da baixa: {qtd_retorno}")  # Alterado para info
            con.commit()
            logger.info("Transação confirmada")
            return qtd_retorno, False
        else:
            logger.warning("A execução da Stored Procedure não retornou resultados.")
            con.rollback()
            return 0, False
    except Exception as e:
        logger.error(f"Erro ao executar baixa de material: {e}")
        if con:
            con.rollback()
        raise
    finally:
        if con:
            con.close()

@app.route('/')
def home():
    """Página inicial do ambiente de produção"""
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sistema de Transferência - Produção</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background-color: #f8f9fa; }
            .container { max-width: 800px; margin: 0 auto; }
            .header { background-color: #28a745; color: white; padding: 20px; border-radius: 8px; text-align: center; }
            .info { background-color: white; padding: 20px; margin: 20px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .endpoint { background-color: #e8f5e8; padding: 10px; margin: 10px 0; border-radius: 4px; }
            .warning { background-color: #d1ecf1; border: 1px solid #bee5eb; padding: 15px; border-radius: 4px; margin: 20px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏭 Ambiente de Produção</h1>
                <p>Sistema de Transferência de Material</p>
            </div>
            
            <div class="warning">
                <strong>ℹ️ INFORMAÇÃO:</strong> Este é o ambiente de produção. 
                Todas as operações são reais e afetam o sistema.
            </div>
            
            <div class="info">
                <h2>📋 Informações do Ambiente</h2>
                <ul>
                    <li><strong>Ambiente:</strong> {{ environment }}</li>
                    <li><strong>Modo Teste:</strong> {{ test_mode }}</li>
                    <li><strong>Rollback Permitido:</strong> {{ allow_rollback }}</li>
                    <li><strong>Banco de Dados:</strong> {{ database }}</li>
                    <li><strong>Porta:</strong> {{ port }}</li>
                </ul>
            </div>
            
            <div class="info">
                <h2>🔗 Endpoints Disponíveis</h2>
                <div class="endpoint">
                    <strong>POST /transfer</strong><br>
                    Executa transferência de material<br>
                    <code>{"etiqueta": "AA123456", "quantidade": 1}</code>
                </div>
                <div class="endpoint">
                    <strong>GET /consulta/&lt;etiqueta&gt;</strong><br>
                    Consulta informações do material
                </div>
                <div class="endpoint">
                    <strong>GET /health</strong><br>
                    Verifica status do serviço
                </div>
                <div class="endpoint">
                    <strong>GET /test</strong><br>
                    Página de testes interativos
                </div>
            </div>
            
            <div class="info">
                <h2>🧪 Funcionalidades de Teste</h2>
                <ul>
                    <li>Adicione <code>?test_rollback=true</code> para reverter transações</li>
                    <li>Logs detalhados em modo DEBUG</li>
                    <li>Auditoria completa de operações</li>
                    <li>CORS habilitado para testes</li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    """, 
    environment=os.getenv('ENVIRONMENT', 'homologacao'),
    test_mode=TEST_MODE,
    allow_rollback=ALLOW_ROLLBACK,
    database=DB_CONFIG['database'],
    port=os.getenv('FLASK_PORT', '5001')
    )

@app.route('/health')
def health():
    """Endpoint de verificação de saúde"""
    try:
        # Testar conexão com banco
        global current_user
        con = get_database_connection(current_user['usuario'], current_user['codigo'])
        con.close()
        
        return jsonify({
            'status': 'healthy',
            'environment': 'homologacao',
            'database': 'connected',
            'timestamp': datetime.now().isoformat(),
            'test_mode': TEST_MODE
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/consulta/<etiqueta>')
def consulta_etiqueta(etiqueta):
    """Endpoint para consultar informações de uma etiqueta"""
    try:
        logger.info(f"Consultando etiqueta: {etiqueta}")
        result = consultar_material(etiqueta)
        
        if result:
            return jsonify({
                'success': True,
                'etiqueta': etiqueta,
                'dados': result,
                'environment': 'homologacao'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Etiqueta não encontrada',
                'etiqueta': etiqueta,
                'environment': 'homologacao'
            }), 404
            
    except Exception as e:
        logger.error(f"Erro na consulta: {e}")
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}',
            'environment': 'homologacao'
        }), 500

@app.route('/api/requisicoes_pendentes', methods=['GET'])
def requisicoes_pendentes():
    """Endpoint para consultar requisições pendentes no sistema - Ambiente de Homologação.
    Retorna: lista de requisições pendentes com detalhes"""
    con = None
    try:
   
        con = get_database_connection()
        cur = con.cursor()
        
        # Query SQL para requisições pendentes
        query = """
            SELECT
                m.codigomoldes as cod_item,
                m.DESCRICAODOMOLDE as material,
                a.DATA as dt_requisicao,
                a1.ALMOXARIFE as dep_origem,
                ps.FISICO,
                a2.ALMOXARIFE as dep_destino,
                v.NREC,
                v.ETIQ,
                v.QUANTIDADE as qt_volume,
                COALESCE(a.QT_ORIGINAL, v.QUANTIDADE) as qt_requisitada,
                m.localizacao
            FROM REQUISICOES_ALMX a
            INNER JOIN DS_ENTRA_ESTOQUE_VOLS v ON v.NREC = a.NREQ AND v.BAIXADO = 0
            INNER JOIN MOVIM_ALMOX a1 ON a1.CODIGOALM = a.ALMX_ORIG
            INNER JOIN PRODUTOS_SALDO ps ON ps.codigomoldes = v.codigomoldes AND ps.CODIGOALM = a1.CODIGOALM
            INNER JOIN MOVIM_ALMOX a2 ON a2.CODIGOALM = a.ALMX_DEST
            INNER JOIN moldes m ON m.codigomoldes = a.CODIGOMOLDES
            WHERE a.data > '1.1.2024'
            ORDER BY a.DATA DESC
        """
        
        cur.execute(query)
        resultados = cur.fetchall()
        
        # Formatar os resultados
        requisicoes = []
        for row in resultados:
       
            localizacao_raw = row[10]
            if localizacao_raw is None:
                localizacao_valor = 'N/A'
            elif isinstance(localizacao_raw, str):
                localizacao_valor = localizacao_raw.strip() if localizacao_raw.strip() else 'N/A'
            else:
                localizacao_valor = str(localizacao_raw).strip() if str(localizacao_raw).strip() else 'N/A'
            
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
                'localizacao': localizacao_valor
            }
            requisicoes.append(requisicao)
        
     
        
        return jsonify({
            'status': 'success',
            'total': len(requisicoes),
            'requisicoes': requisicoes,
            'environment': 'homologacao'
        }), 200
            
    except fdb.DatabaseError as db_error:
      
        return jsonify({
            'status': 'error',
            'erro': 'Erro no banco de dados.',
            'detalhes': str(db_error),
            'environment': 'homologacao'
        }), 500
    except Exception as e:
      
        return jsonify({
            'status': 'error',
            'erro': 'Ocorreu um erro interno no servidor.',
            'detalhes': str(e),
            'environment': 'homologacao'
        }), 500
    finally:
        if con:
            con.close()

@app.route('/api/consulta_material', methods=['POST'])
def consulta_material_api():
    """Endpoint para consultar material via QR Code - compatível com frontend"""
    try:
        data = request.get_json()
        codigo = data.get('codigo') if data else None
        
        if not codigo:
            return jsonify({
                'erro': 'O campo "codigo" é obrigatório.'
            }), 400
        
        logger.info(f"[CONSULTA_MATERIAL] Consultando código: {codigo}")
        result = consultar_material(codigo)
        
        if result:
            # Verificar se os dados essenciais estão presentes
            codigo_material = result[0] if len(result) > 0 else None
            descricao_material = result[1] if len(result) > 1 else None
            
            # Se código ou descrição são None/vazios ou contêm 'N/A', considerar como material não encontrado
            if (not codigo_material or not descricao_material or 
                str(codigo_material).upper() == 'N/A' or str(descricao_material).upper() == 'N/A' or
                codigo_material == 'null' or descricao_material == 'null'):
                logger.warning(f"[CONSULTA_MATERIAL] Material INVÁLIDO - código: {codigo_material}, descrição: {descricao_material}")
                return jsonify({'erro': 'Nenhum material encontrado para o código lido.'}), 404
            
            # result é uma tupla, vamos converter para dicionário
            # Retornando a mesma estrutura que o backend de produção
            
            # Adiciona verificação para evitar erro de NoneType com round()
            qt_etiq_formatada = round(result[4], 2) if len(result) > 4 and result[4] is not None else None
            qt_rec_formatada = round(result[5], 2) if len(result) > 5 and result[5] is not None else None
            
            material = {
                'codigomoldes': codigo_material,
                'descricao': descricao_material,
                'tipo': result[2] if len(result) > 2 else '',
                'proced': result[3] if len(result) > 3 else '',
                'qt_etiq': qt_etiq_formatada,
                'qt_rec': qt_rec_formatada,
                'localizacao': result[6] if len(result) > 6 else '',
                'mensagem': result[7] if len(result) > 7 else '',
                'dep_origem': result[8] if len(result) > 8 else '',
                'dep_destino': result[9] if len(result) > 9 else '',
                'unidade': result[10] if len(result) > 10 else '',
                'nreq': result[11] if len(result) > 11 else '',
                'saldo': round(result[15], 2) if len(result) > 15 and result[15] is not None else 0
            }
            
            logger.info(f"[CONSULTA_MATERIAL] Material VÁLIDO formatado para código: {codigo}")
            return jsonify(material), 200
        else:
            return jsonify({
                'erro': 'Material não encontrado'
            }), 404
            
    except Exception as e:
        logger.error(f"Erro na consulta de material: {e}")
        return jsonify({
            'erro': f'Erro interno: {str(e)}'
        }), 500

@app.route('/api/transferencia_material', methods=['POST'])
def transferencia_material():
    con = None  # Inicializa a conexão como None para acesso no finally
    try:
        data = request.json
        usuario = data.get('usuario') # Pega o usuário do corpo da requisição
        codigo_usuario = data.get('codigo_usuario') # Pega o código do usuário do corpo da requisição

        if not usuario or not codigo_usuario:
            return jsonify({'sucesso': False, 'erro': 'Usuário não fornecido'}), 400

        print(f"Usuário fornecido: {usuario}")
        
        codigo = data.get('codigo')
        if not codigo:
            return jsonify({'sucesso': False, 'erro': 'Código não fornecido'}), 400

        logger.info(f"Transferência solicitada por: {usuario} (Código: {codigo_usuario})")
        
        con = get_database_connection()
        cursor = con.cursor()
        
        logger.info(f"Chamando SP_BAIXA_REQUISICAO_MAT_USER com código: {codigo} e usuário: {codigo_usuario}")
        cursor.callproc('SP_BAIXA_REQUISICAO_MAT_USER', (codigo, codigo_usuario))
        result = cursor.fetchone()
        
        if result:
            qtd_retorno = result[0]
            con.commit()
            log_audit('transferencia_material', codigo, 1, qtd_retorno)
            return jsonify({
                'sucesso': True,
                'mensagem': f"Transferência executada com sucesso para código: {codigo}",
                'quantidade_transferida': qtd_retorno
            }), 200
        else:
            con.rollback()
            logger.warning("A execução da Stored Procedure não retornou resultados.")
            return jsonify({
                'sucesso': False,
                'erro': f"Falha na transferência para o código {codigo}."
            }), 400
    
    except Exception as e:
        if con:
            con.rollback()
        logger.error(f"Erro na API de transferência: {e}")
        return jsonify({
            'sucesso': False,
            'erro': f"Ocorreu um erro interno no servidor: {e}"
        }), 500
    
    finally:
        if con:
            con.close()


def transfer():
    """Endpoint principal para transferência de material"""
    try:
        data = request.get_json()
        
        if not data or 'etiqueta' not in data or 'quantidade' not in data:
            return jsonify({
                'success': False,
                'message': 'Dados inválidos. Necessário: etiqueta e quantidade',
                'environment': 'homologacao'
            }), 400
        
        etiqueta = data['etiqueta']
        quantidade = data['quantidade']
        
        logger.info(f"Iniciando transferência - Etiqueta: {etiqueta}, Quantidade: {quantidade}")
        
        # Executar a baixa
        qtd_retorno, was_rollback = executar_baixa_material(etiqueta, quantidade)
        
        # Log de auditoria
        log_audit('transfer', etiqueta, quantidade, qtd_retorno)
        
        # Processar resultado
        if qtd_retorno is None:
            return jsonify({
                'success': False,
                'message': 'Erro na execução da stored procedure',
                'environment': 'homologacao',
                'rollback': was_rollback
            }), 500
        
        elif qtd_retorno > 0:
            message = f"Baixa efetuada com sucesso! Quantidade: {qtd_retorno}"
            if was_rollback:
                message += " (TESTE - transação revertida)"
            
            return jsonify({
                'success': True,
                'message': message,
                'quantidade_baixada': qtd_retorno,
                'etiqueta': etiqueta,
                'tipo': 'baixa_completa',
                'environment': 'homologacao',
                'rollback': was_rollback
            })
        
        elif qtd_retorno == -1:
            return jsonify({
                'success': False,
                'message': 'Etiqueta inválida',
                'environment': 'homologacao'
            }), 400
        
        elif qtd_retorno == -2:
            return jsonify({
                'success': False,
                'message': 'Etiqueta não encontrada',
                'environment': 'homologacao'
            }), 404
        
        elif qtd_retorno == -3:
            return jsonify({
                'success': False,
                'message': 'Produto já baixado',
                'environment': 'homologacao'
            }), 400
        
        elif qtd_retorno == -4:
            message = "Baixa efetuada - parcial da requisição"
            if was_rollback:
                message += " (TESTE - transação revertida)"
            
            return jsonify({
                'success': True,
                'message': message,
                'etiqueta': etiqueta,
                'tipo': 'baixa_parcial',
                'environment': 'homologacao',
                'rollback': was_rollback
            })
        
        else:
            return jsonify({
                'success': False,
                'message': f'Código de retorno não reconhecido: {qtd_retorno}',
                'environment': 'homologacao'
            }), 500
    
    except Exception as e:
        logger.error(f"Erro na transferência: {e}")
        logger.error(traceback.format_exc())
        
        log_audit('transfer_error', data.get('etiqueta', 'unknown'), data.get('quantidade', 0), str(e))
        
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}',
            'environment': 'homologacao'
        }), 500

@app.route('/api/login_auth', methods=['POST'])
def login_auth():
    """
    Endpoint para autenticação de usuário usando stored procedure Login_pwd
    Parâmetros: user_id (int), password (string)
    Retorna: auth_code se sucesso, null se falha
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        password = data.get('password')
        
        if not user_id or not password:
            return jsonify({
                'success': False,
                'message': 'Usuário e senha são obrigatórios'
            }), 400
        
        logger.info(f"[LOGIN_AUTH] Tentativa de login para usuário: {user_id}")
        
        # Para login, usar conexão sem SET_USER inicialmente
        con = get_database_connection()
        cur = con.cursor()
        
        # Executar stored procedure Login_pwd
        query = "select auth from Login_pwd(?, ?)"
        cur.execute(query, (int(user_id), str(password)))
        result = cur.fetchone()
        
        if result and result[0] is not None:
            auth_code = result[0]
            
            # Login válido apenas se auth_code == user_id
            # No endpoint /api/login_auth, após login sucesso:
            if auth_code == int(user_id):
                # Login bem-sucedido - gerar token JWT
                access_token = create_access_token(identity=user_id)
                
                logger.info(f"[LOGIN_AUTH] Login bem-sucedido para usuário {user_id}, auth_code: {auth_code}")
                log_audit('login', user_id, 1, f'sucesso_auth_{auth_code}', request.remote_addr)
                
                return jsonify({
                    'success': True,
                    'auth_code': auth_code,
                    'token': access_token,
                    'usuario': {
                        'codigo': user_id,
                        'nome': str(user_id)
                    }
                })
            elif auth_code == 0:
                # Senha incorreta
                logger.warning(f"[LOGIN_AUTH] Senha incorreta para usuário {user_id}")
                log_audit('login', user_id, 1, 'senha_incorreta', request.remote_addr)
                
                return jsonify({
                    'success': False,
                    'message': 'Credenciais inválidas'
                }), 401
            else:
                # Auth code inválido (não corresponde ao user_id)
                logger.warning(f"[LOGIN_AUTH] Auth code inválido para usuário {user_id}, auth_code: {auth_code}")
                log_audit('login', user_id, 1, f'auth_invalido_{auth_code}', request.remote_addr)
                
                return jsonify({
                    'success': True,
                    'auth_code': auth_code,
                    'message': 'Login realizado com sucesso'
                })
        else:
            # Procedure retornou NULL (usuário não encontrado ou erro)
            logger.warning(f"[LOGIN_AUTH] Falha no login para usuário {user_id} (usuário não encontrado ou erro)")
            log_audit('login', user_id, 1, 'falha', request.remote_addr)
            
            return jsonify({
                'success': False,
                'message': 'Credenciais inválidas'
            }), 401
            
    except Exception as e:
        logger.error(f"[LOGIN_AUTH] Erro na autenticação: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Erro interno do servidor'
        }), 500
    finally:
        try:
            if 'cur' in locals() and cur:
                cur.close()
        except:
            pass
        try:
            if 'con' in locals() and con:
                con.close()
        except:
            pass

@app.route('/login')
def login_page():
    """Página de login de teste"""
    try:
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        login_file_path = os.path.join(current_dir, 'login_test.html')
        with open(login_file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Arquivo login_test.html não encontrado", 404
    except Exception as e:
        logger.error(f"Erro ao carregar página de login: {e}")
        return f"Erro interno: {str(e)}", 500

@app.route('/test')
def test_page():
    """Página de testes interativos"""
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Testes - Produção</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background-color: #f0f8ff; }
            .container { max-width: 1000px; margin: 0 auto; }
            .test-section { background-color: white; padding: 20px; margin: 20px 0; border-radius: 8px; }
            button { background-color: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
            button:hover { background-color: #0056b3; }
            input, select { padding: 8px; margin: 5px; border: 1px solid #ddd; border-radius: 4px; }
            .result { background-color: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 4px; white-space: pre-wrap; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🧪 Página de Testes - Produção</h1>
            
            <div class="test-section">
                <h2>Teste de Transferência</h2>
                <input type="text" id="etiqueta" placeholder="Etiqueta (ex: AA161722)" value="AA161722">
                <input type="number" id="quantidade" placeholder="Quantidade" value="1">
                <label><input type="checkbox" id="rollback"> Modo Teste (Rollback)</label><br><br>
                <button onclick="testarTransferencia()">Executar Transferência</button>
                <div id="resultTransfer" class="result"></div>
            </div>
            
            <div class="test-section">
                <h2>Consulta de Material</h2>
                <input type="text" id="etiquetaConsulta" placeholder="Etiqueta" value="AA161722">
                <button onclick="consultarMaterial()">Consultar</button>
                <div id="resultConsulta" class="result"></div>
            </div>
            
            <div class="test-section">
                <h2>Verificação de Saúde</h2>
                <button onclick="verificarSaude()">Verificar Status</button>
                <div id="resultSaude" class="result"></div>
            </div>
        </div>
        
        <script>
            async function testarTransferencia() {
                const etiqueta = document.getElementById('etiqueta').value;
                const quantidade = document.getElementById('quantidade').value;
                const rollback = document.getElementById('rollback').checked;
                
                const url = rollback ? '/transfer?test_rollback=true' : '/transfer';
                
                try {
                    const response = await fetch(url, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ etiqueta, quantidade: parseInt(quantidade) })
                    });
                    
                    const result = await response.json();
                    document.getElementById('resultTransfer').textContent = JSON.stringify(result, null, 2);
                } catch (error) {
                    document.getElementById('resultTransfer').textContent = 'Erro: ' + error.message;
                }
            }
            
            async function consultarMaterial() {
                const etiqueta = document.getElementById('etiquetaConsulta').value;
                
                try {
                    const response = await fetch(`/consulta/${etiqueta}`);
                    const result = await response.json();
                    document.getElementById('resultConsulta').textContent = JSON.stringify(result, null, 2);
                } catch (error) {
                    document.getElementById('resultConsulta').textContent = 'Erro: ' + error.message;
                }
            }
            
            async function verificarSaude() {
                try {
                    const response = await fetch('/health');
                    const result = await response.json();
                    document.getElementById('resultSaude').textContent = JSON.stringify(result, null, 2);
                } catch (error) {
                    document.getElementById('resultSaude').textContent = 'Erro: ' + error.message;
                }
            }
        </script>
    </body>
    </html>
    """, 
    environment=os.getenv('ENVIRONMENT', 'homologacao'),
    test_mode=TEST_MODE,
    allow_rollback=ALLOW_ROLLBACK,
    database=DB_CONFIG['database'],
    port=os.getenv('FLASK_PORT', '5001')
    )

@app.route('/api/usuarios_login', methods=['GET'])
def usuarios_login_api():
    """API para consultar usuários com LOGON_QR = 1"""
    try:
        # Usar dados do usuário logado se disponíveis
        global current_user
        con = get_database_connection()
        cursor = con.cursor()
        
        # Query SQL conforme especificado
        query = """
            SELECT r.CODIGO, r.USUARIO, r.LOGON_QR 
            FROM USUARIOS r 
            WHERE r.LOGON_QR = 1
        """
        
        logger.debug(f"Executando query: {query}")
        cursor.execute(query)
        result = cursor.fetchall()
        
        # Converter resultado para lista de dicionários
        usuarios = []
        for row in result:
            usuarios.append({
                'codigo': row[0],
                'usuario': row[1],
                'logon_qr': row[2]
            })
        
        logger.info(f"Encontrados {len(usuarios)} usuários com LOGON_QR = 1")
        
        return jsonify({
            'success': True,
            'usuarios': usuarios,
            'total': len(usuarios)
        })
        
    except Exception as e:
        logger.error(f"Erro ao consultar usuários: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        if 'con' in locals():
            con.close()

if __name__ == '__main__':
    # Configurações específicas para produção - porta fixa 5000
    port = 5000  # Porta fixa para celulares corporativos
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Iniciando servidor de produção na porta {port}")
    logger.info(f"Modo teste: {TEST_MODE}")
    logger.info(f"Rollback permitido: {ALLOW_ROLLBACK}")
    logger.info(f"Banco de dados: {DB_CONFIG['database']}")
    
    # Verificar se certificados SSL existem
    ssl_cert = os.getenv('SSL_CERT_PATH', 'cert.pem')
    ssl_key = os.getenv('SSL_KEY_PATH', 'key.pem')
    
    if ssl_cert and ssl_key and os.path.exists(ssl_cert) and os.path.exists(ssl_key):
        logger.info("Iniciando com SSL usando certificados personalizados")
        logger.info(f"Certificados: {ssl_cert}, {ssl_key}")
        # Configuração SSL mais robusta para celulares
        import ssl
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(ssl_cert, ssl_key)
        # Configurações para melhor compatibilidade com celulares
        context.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS')
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        context.maximum_version = ssl.TLSVersion.TLSv1_3
        # Permitir renegociação para melhor compatibilidade
        context.options |= ssl.OP_CIPHER_SERVER_PREFERENCE
        app.run(host=host, port=port, debug=debug, ssl_context=context)
    else:
        logger.info("Certificados não encontrados, iniciando com SSL adhoc (self-signed)")
        logger.warning("Para produção, use certificados SSL válidos")
        # Configuração adhoc mais compatível
        import ssl
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        app.run(host=host, port=port, debug=debug, ssl_context='adhoc')
