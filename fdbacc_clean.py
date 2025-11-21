# -*- coding: utf-8 -*-
# Importa a biblioteca Flask para criar o servidor web.
# 'jsonify' é para converter dicionários Python em respostas JSON.
# 'request' é para acessar os dados enviados do front-end.
from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import logging
from logging.handlers import RotatingFileHandler

# Importa as bibliotecas para conexão com o banco de dados Firebird.
# Você precisará instalar esta biblioteca com: pip install fdb
import fdb

app = Flask(__name__)
CORS(app)  # Habilita CORS para todas as rotas

# --- Configuração do sistema de logging ---
def configurar_logging():
    """
    Configura o sistema de logging da aplicação.
    """
    # Criar diretório de logs se não existir (ANTES de criar o handler)
    os.makedirs('logs', exist_ok=True)
    
    # Nível de log baseado na variável de ambiente
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    
    # Configuração do formato de log
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Handler para arquivo com rotação
    file_handler = RotatingFileHandler(
        'logs/app.log', maxBytes=10240000, backupCount=10
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(getattr(logging, log_level, logging.INFO))
    
    # Handler para console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(getattr(logging, log_level, logging.INFO))
    
    # Configurar logger da aplicação
    app.logger.setLevel(getattr(logging, log_level, logging.INFO))
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    
    app.logger.info(f"Sistema de logging configurado - Nível: {log_level}")

# Configurar logging
configurar_logging()

# --- Função para verificar stored procedures ---
def verificar_stored_procedure(con, nome_procedure):
    """
    Verifica se uma stored procedure existe no banco de dados.
    Retorna True se existe, False caso contrário.
    """
    try:
        cur = con.cursor()
        cur.execute("""
            SELECT COUNT(*) FROM RDB$PROCEDURES 
            WHERE RDB$PROCEDURE_NAME = ?
        """, (nome_procedure.upper(),))
        resultado = cur.fetchone()
        return resultado[0] > 0 if resultado else False
    except Exception as e:
        app.logger.error(f"Erro ao verificar stored procedure {nome_procedure}: {e}")
        return False

# --- Configuração do banco de dados Firebird ---
# Usa variáveis de ambiente com valores padrão para desenvolvimento
DB_PATH = os.getenv('DB_PATH', 'e:/gdb/retesp.fdb')
DB_HOST = os.getenv('DB_HOST', '192.168.0.8')
DB_USER = os.getenv('DB_USER', 'SYSDBA')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'a')
DB_ENCODING = os.getenv('DB_ENCODING', 'LATIN1')

# --- Rotas básicas do sistema ---
@app.route('/')
def index():
    """
    Página principal do sistema.
    """
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sistema de Transferência de Material - Produção</title>
        <meta charset="utf-8">
    </head>
    <body>
        <h1>Sistema de Transferência de Material</h1>
        <h2>Ambiente: Produção</h2>
        <p>Sistema operacional e funcionando.</p>
        <ul>
            <li><a href="/api/test_db">Testar Banco de Dados</a></li>
        </ul>
    </body>
    </html>
    '''

@app.route('/health')
def health_check():
    """
    Endpoint de health check para monitoramento.
    """
    try:
        # Testa conexão com banco
        with fdb.connect(
            database=DB_PATH,
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            charset=DB_ENCODING
        ) as con:
            cur = con.cursor()
            cur.execute("SELECT 1 FROM RDB$DATABASE")
            cur.fetchone()
        
        return jsonify({
            'status': 'healthy',
            'environment': 'producao',
            'database': 'connected',
            'test_mode': False
        })
        
    except Exception as e:
        app.logger.error(f"[ERRO] Health check falhou: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'environment': 'producao',
            'database': 'disconnected',
            'error': str(e)
        }), 500

# --- Endpoint de teste para conexão com banco de dados ---
@app.route('/api/test_db', methods=['GET'])
def test_db():
    """
    Endpoint para testar a conectividade com o banco de dados Firebird.
    Retorna: {"status": "success", "message": "..."} ou {"status": "error", "message": "..."}
    """
    try:
        with fdb.connect(
            database=DB_PATH,
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            charset=DB_ENCODING
        ) as con:
            cur = con.cursor()
            
            # Executa uma consulta simples para testar a conexão
            cur.execute("SELECT 1 FROM RDB$DATABASE")
            resultado = cur.fetchone()
            
            if resultado:
                return jsonify({
                    'status': 'success',
                    'message': 'Conexão com banco de dados estabelecida com sucesso!',
                    'database': DB_PATH,
                    'host': DB_HOST,
                    'user': DB_USER
                }), 200
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Falha ao executar consulta de teste'
                }), 500
                
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao conectar com o banco de dados: {str(e)}',
            'database': DB_PATH,
            'host': DB_HOST,
            'user': DB_USER
        }), 500

# --- API para consulta de material ---
@app.route('/api/consulta_material', methods=['POST'])
def consulta_material():
    """
    Endpoint para consultar os dados de um material a partir de um QR Code.
    Recebe: {"codigo": "CODIGO_QR"}
    Retorna: {"material": {...}} ou {"erro": "Mensagem de erro"}
    """
    con = None  # Inicializa a variável de conexão
    try:
        data = request.json
        codigo_lido = data.get('codigo')
        
        # Log detalhado do código recebido
        app.logger.info(f"[CONSULTA] Código recebido: '{codigo_lido}' (tipo: {type(codigo_lido)})")
        
        if not codigo_lido:
            app.logger.warning("[CONSULTA] ERRO: Campo código vazio ou ausente")
            return jsonify({'erro': 'O campo "codigo" é obrigatório.'}), 400
        
        # Validação de tamanho do código para evitar overflow numérico
        codigo_str = str(codigo_lido).strip()
        if len(codigo_str) > 20:  # Limite para evitar overflow na stored procedure
            app.logger.warning(f"[CONSULTA] ERRO: Código muito longo ({len(codigo_str)} caracteres): '{codigo_str}'")
            return jsonify({'erro': 'Código QR muito longo. Máximo permitido: 20 caracteres.'}), 400
        
        # Verificação se é um código numérico muito grande
        if codigo_str.isdigit() and len(codigo_str) > 10:
            app.logger.warning(f"[CONSULTA] ERRO: Código numérico muito grande: '{codigo_str}'")
            return jsonify({'erro': 'Código numérico muito grande. Verifique se o código está correto.'}), 400

        with fdb.connect(
            database=DB_PATH,
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            charset=DB_ENCODING
        ) as con:
            # Verifica se a stored procedure existe
            if not verificar_stored_procedure(con, 'CONSULTA_QR_MATERIAL'):
                app.logger.error("[ERRO] Stored procedure CONSULTA_QR_MATERIAL não encontrada")
                return jsonify({'erro': 'Erro interno: stored procedure não encontrada.'}), 500
            
            cur = con.cursor()
            
            # Executa a chamada da stored procedure.
            cur.callproc('CONSULTA_QR_MATERIAL', (codigo_lido,))
            resultado_sp = cur.fetchone()
            
            # Garante que a transação seja finalizada, mesmo em consultas.
            con.commit()
            
            if resultado_sp:
                # Log detalhado do resultado da stored procedure
                app.logger.debug(f"[CONSULTA] Resultado SP encontrado: {resultado_sp}")
                
                # Verificar se os dados essenciais estão presentes
                codigo_material = resultado_sp[0]
                descricao_material = resultado_sp[1]
                
                # Se código ou descrição são None/vazios, considerar como material não encontrado
                if not codigo_material or not descricao_material:
                    app.logger.warning(f"[CONSULTA] Material INVÁLIDO - código: {codigo_material}, descrição: {descricao_material}")
                    return jsonify({'erro': 'Nenhum material encontrado para o código lido.'}), 404
                
                # Adiciona verificação para evitar erro de NoneType com round()
                # Correção aplicada: verificação adicional de índice para compatibilidade
                qt_etiq_formatada = round(resultado_sp[4], 2) if len(resultado_sp) > 4 and resultado_sp[4] is not None else None
                qt_rec_formatada = round(resultado_sp[5], 2) if len(resultado_sp) > 5 and resultado_sp[5] is not None else None
                
                material = {
                    'codigomoldes': codigo_material,
                    'descricao': descricao_material,
                    'tipo': resultado_sp[2],
                    'proced': resultado_sp[3],
                    'qt_etiq': qt_etiq_formatada,
                    'qt_rec': qt_rec_formatada,
                    'localizacao': resultado_sp[6],
                    'mensagem': resultado_sp[7],
                    'dep_origem': resultado_sp[8],
                    'dep_destino': resultado_sp[9],
                    'unidade': resultado_sp[10],
                    'nreq': resultado_sp[11]
                }
                
                app.logger.info(f"[CONSULTA] Material VÁLIDO formatado para código: {codigo_lido}")
                return jsonify(material), 200
            else:
                app.logger.warning(f"[CONSULTA] NENHUM RESULTADO encontrado para código: '{codigo_lido}'")
                return jsonify({'erro': 'Nenhum material encontrado para o código lido.'}), 404
    except fdb.DatabaseError as db_error:
        # Em caso de erro do banco de dados, a transação é desfeita.
        try:
            if con:
                con.rollback()
        except:
            pass  # Ignora erros no rollback se a conexão já estiver fechada
        app.logger.error(f"Erro no banco de dados (consulta_material): {db_error}")
        return jsonify({'erro': 'Erro no banco de dados.', 'detalhes': str(db_error)}), 500
    except Exception as e:
        app.logger.error(f"Erro inesperado (consulta_material): {e}")
        return jsonify({'erro': 'Ocorreu um erro interno no servidor.', 'detalhes': str(e)}), 500

# --- API para consulta de requisições pendentes ---
@app.route('/api/requisicoes_pendentes', methods=['GET'])
def requisicoes_pendentes():
    """
    Endpoint para consultar requisições pendentes no sistema - Ambiente de Produção.
    Retorna: lista de requisições pendentes com detalhes
    """
    try:
        app.logger.info("[REQUISICOES_PENDENTES] Iniciando consulta de requisições pendentes - PRODUÇÃO")
        
        with fdb.connect(
            database=DB_PATH,
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            charset=DB_ENCODING
        ) as con:
            cur = con.cursor()
            
            # Query SQL para requisições pendentes
            query = """
                SELECT 
                    m.codigomoldes as cod_item, 
                    m.DESCRICAODOMOLDE as material, 
                    r.DT_REQUISICAO as dt_requisicao,
                    dep_origem.DESCRICAO as dep_origem,
                    dep_destino.DESCRICAO as dep_destino,
                    r.NREC as nrec,
                    r.ETIQ as etiq,
                    r.QT_VOLUME as qt_volume,
                    r.QT_REQUISITADA as qt_requisitada
                FROM REQUISICOES r
                INNER JOIN MOLDES m ON r.COD_ITEM = m.CODIGOMOLDES
                INNER JOIN DEPARTAMENTOS dep_origem ON r.DEP_ORIGEM = dep_origem.CODIGO
                INNER JOIN DEPARTAMENTOS dep_destino ON r.DEP_DESTINO = dep_destino.CODIGO
                WHERE r.STATUS = 'P'
                ORDER BY r.DT_REQUISICAO DESC
            """
            
            app.logger.info("[REQUISICOES_PENDENTES] Executando consulta SQL")
            cur.execute(query)
            resultados = cur.fetchall()
            
            # Formatação dos resultados
            requisicoes = []
            for row in resultados:
                requisicao = {
                    'cod_item': row[0],
                    'material': row[1],
                    'dt_requisicao': row[2].strftime('%d/%m/%Y') if row[2] else None,
                    'dep_origem': row[3],
                    'dep_destino': row[4],
                    'nrec': row[5],
                    'etiq': row[6],
                    'qt_volume': float(row[7]) if row[7] else 0.0,
                    'qt_requisitada': float(row[8]) if row[8] else 0.0
                }
                requisicoes.append(requisicao)
            
            app.logger.info(f"[REQUISICOES_PENDENTES] Encontradas {len(requisicoes)} requisições pendentes")
            
            return jsonify({
                'status': 'success',
                'total': len(requisicoes),
                'requisicoes': requisicoes
            }), 200
            
    except fdb.DatabaseError as db_error:
        app.logger.error(f"Erro no banco de dados (requisicoes_pendentes): {db_error}")
        return jsonify({
            'status': 'error',
            'erro': 'Erro no banco de dados.',
            'detalhes': str(db_error)
        }), 500
    except Exception as e:
        app.logger.error(f"Erro inesperado (requisicoes_pendentes): {e}")
        return jsonify({
            'status': 'error',
            'erro': 'Ocorreu um erro interno no servidor.',
            'detalhes': str(e)
        }), 500

# --- API para transferência de material ---
@app.route('/api/transferencia_material', methods=['POST'])
def transferencia_material():
    """
    Endpoint para confirmar a transferência e baixa de material utilizando
    a nova stored procedure SP_BAIXA_REQUISICAO_MAT.
    """
    con = None  # Inicializa a variável de conexão
    try:
        data = request.json
        codigo_lido = data.get('codigo')
        
        # Log detalhado dos dados recebidos
        app.logger.info(f"[TRANSFERENCIA] Dados recebidos para processamento")
        app.logger.info(f"[TRANSFERENCIA] Código extraído: '{codigo_lido}' (tipo: {type(codigo_lido)})")

        if not codigo_lido:
            app.logger.warning("[TRANSFERENCIA] ERRO: Campo código vazio ou ausente")
            return jsonify({'erro': 'O campo "codigo" é obrigatório.'}), 400
        
        # Validação de tamanho do código para evitar overflow numérico
        codigo_str = str(codigo_lido).strip()
        if len(codigo_str) > 20:  # Limite para evitar overflow na stored procedure
            app.logger.warning(f"[TRANSFERENCIA] ERRO: Código muito longo ({len(codigo_str)} caracteres): '{codigo_str}'")
            return jsonify({'erro': 'Código QR muito longo. Máximo permitido: 20 caracteres.'}), 400
        
        # Verificação se é um código numérico muito grande
        if codigo_str.isdigit() and len(codigo_str) > 10:
            app.logger.warning(f"[TRANSFERENCIA] ERRO: Código numérico muito grande: '{codigo_str}'")
            return jsonify({'erro': 'Código numérico muito grande. Verifique se o código está correto.'}), 400

        with fdb.connect(
            database=DB_PATH,
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            charset=DB_ENCODING
        ) as con:
            # Verifica se a stored procedure existe
            if not verificar_stored_procedure(con, 'SP_BAIXA_REQUISICAO_MAT'):
                app.logger.error("[ERRO] Stored procedure SP_BAIXA_REQUISICAO_MAT não encontrada")
                return jsonify({'erro': 'Erro interno: stored procedure não encontrada.'}), 500
            
            cur = con.cursor()
            
            # Log da execução da stored procedure
            app.logger.info(f"[TRANSFERENCIA] Executando SP_BAIXA_REQUISICAO_MAT com código: '{codigo_lido}'")
            
            # Chama a nova stored procedure para realizar a baixa.
            # Esta procedure já faz todas as validações e atualizações.
            cur.callproc('SP_BAIXA_REQUISICAO_MAT', (codigo_lido,))
            resultado_sp = cur.fetchone()
            
            qtd_retorno = resultado_sp[0]
            nrec = resultado_sp[1]

            # Lógica para tratar os códigos de retorno da stored procedure
            if qtd_retorno == -1:
                return jsonify({'erro': 'Etiqueta inválida ou em branco.'}), 400
            elif qtd_retorno == -2:
                return jsonify({'erro': 'Etiqueta não encontrada.'}), 404
            elif qtd_retorno == -3:
                return jsonify({'erro': 'Produto já baixado.'}), 400
            elif qtd_retorno == -4:
                return jsonify({'mensagem': 'Baixa efetuada - parcial da requisição', 'codigo_lido': qrcode, 'tipo': 'baixa_parcial'}), 200
            elif qtd_retorno > 0:
                con.commit()
                app.logger.info(f"[TRANSFERENCIA] BAIXA PARCIAL - Material: '{codigo_lido}', Sobra: {qtd_retorno}")
                return jsonify({
                    'mensagem': f"Baixa parcial. Sobrariam {qtd_retorno} unidades.",
                    'codigo_lido': codigo_lido,
                    'qtd_retorno': qtd_retorno,
                    'nrec': nrec
                }), 200
            else: # qtd_retorno == 0
                con.commit()
                app.logger.info(f"[TRANSFERENCIA] SUCESSO - Baixa completa do material: '{codigo_lido}'")
                return jsonify({
                    'mensagem': 'Baixa completa confirmada!',
                    'codigo_lido': codigo_lido,
                    'qtd_retorno': qtd_retorno,
                    'nrec': nrec
                }), 200

    except fdb.DatabaseError as db_error:
        # A exceção `fdb.DatabaseError` é capturada e a transação é desfeita.
        try:
            if con:
                con.rollback()
        except:
            pass  # Ignora erros no rollback se a conexão já estiver fechada
        
        # Tratamento específico para erro -836 (EX_NECESSITA_MAIS_VOLUME)
        error_str = str(db_error)
        if "-836" in error_str and "EX_NECESSITA_MAIS_VOLUME" in error_str:
            app.logger.info(f"[TRANSFERENCIA] BAIXA PARCIAL DETECTADA - Código: '{codigo_lido}' - Erro -836")
            return jsonify({
                'mensagem': 'Baixa parcial registrada. A quantidade da requisição é maior que a da etiqueta.',
                'codigo_lido': codigo_lido,
                'tipo': 'baixa_parcial',
                'detalhes': 'A quantidade da etiqueta foi totalmente baixada, mas a requisição ainda precisa de mais material.'
            }), 200
        
        app.logger.error(f"Erro no banco de dados durante a transferência: {db_error}")
        return jsonify({'erro': 'Erro no banco de dados durante a transferência.', 'detalhes': str(db_error)}), 500
    except Exception as e:
        app.logger.error(f"Erro inesperado (transferencia_material): {e}")
        return jsonify({'erro': 'Ocorreu um erro interno no servidor.', 'detalhes': str(e)}), 500



if __name__ == '__main__':
    # Configuração do servidor usando variáveis de ambiente
    debug_mode = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', '5000'))
    
    # Configuração SSL - verifica se os certificados existem
    cert_file = os.getenv('SSL_CERT', 'cert.pem')
    key_file = os.getenv('SSL_KEY', 'key.pem')
    
    ssl_context = None
    if os.path.exists(cert_file) and os.path.exists(key_file):
        ssl_context = (cert_file, key_file)
        app.logger.info(f"[INFO] Servidor iniciando com SSL em https://{host}:{port}")
    else:
        app.logger.warning(f"[AVISO] Certificados SSL não encontrados. Servidor iniciando sem SSL em http://{host}:{port}")
        app.logger.warning(f"[AVISO] Para usar SSL, certifique-se de que {cert_file} e {key_file} existem")
    
    if debug_mode:
        app.logger.warning("[AVISO] Modo DEBUG ativado. Desative em produção definindo FLASK_DEBUG=false")
    
    app.run(debug=debug_mode, host=host, port=port, ssl_context=ssl_context)
