from flask import Flask, send_file, request, render_template, jsonify, redirect
from datetime import datetime
import psycopg2
import psycopg2.extras
import os
import urllib.parse
from config import config

app = Flask(__name__)
app.config.from_object(config)

# Configuração do banco de dados PostgreSQL
DATABASE_CONFIG = config.DATABASE_CONFIG

def get_db_connection():
    """Cria uma conexão com o banco PostgreSQL"""
    try:
        conn = psycopg2.connect(
            host=DATABASE_CONFIG['HOST'],
            database=DATABASE_CONFIG['NAME'],
            user=DATABASE_CONFIG['USER'],
            password=DATABASE_CONFIG['PASSWORD'],
            port=DATABASE_CONFIG['PORT']
        )
        return conn
    except psycopg2.Error as e:
        print(f"Erro ao conectar ao PostgreSQL: {e}")
        return None

def init_db():
    """Inicializa o banco de dados com as tabelas necessárias"""
    conn = get_db_connection()
    if not conn:
        print("Não foi possível conectar ao banco de dados")
        return
    
    cursor = conn.cursor()
    try:
        # Tabela para rastreamento de imagens
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS image_views (
                id SERIAL PRIMARY KEY,
                id_fatura VARCHAR(255) NOT NULL,
                ip_address VARCHAR(45),
                user_agent TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                referer TEXT
            )
        ''')
        
        # Tabela para rastreamento de boletos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS boleto_views (
                id SERIAL PRIMARY KEY,
                empresa VARCHAR(50) NOT NULL,
                codigo_boleto VARCHAR(255) NOT NULL,
                id_fatura VARCHAR(255),
                ip_address VARCHAR(45),
                user_agent TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                referer TEXT
            )
        ''')
        
        conn.commit()
        print("Tabelas image_views e boleto_views criadas/verificadas com sucesso!")
    except psycopg2.Error as e:
        print(f"Erro ao criar tabelas: {e}")
    finally:
        cursor.close()
        conn.close()

def log_image_view(id_fatura):
    """Registra uma visualização da imagem no banco de dados"""
    conn = get_db_connection()
    if not conn:
        print("Não foi possível conectar ao banco para registrar visualização")
        return
    
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO image_views (id_fatura, ip_address, user_agent, referer)
            VALUES (%s, %s, %s, %s)
        ''', (
            id_fatura,
            request.remote_addr,
            request.headers.get('User-Agent', ''),
            request.headers.get('Referer', '')
        ))
        
        conn.commit()
        print(f"Visualização registrada para fatura: {id_fatura}")
    except psycopg2.Error as e:
        print(f"Erro ao registrar visualização: {e}")
    finally:
        cursor.close()
        conn.close()

@app.route('/')
def index():
    """Página principal com estatísticas"""
    conn = get_db_connection()
    if not conn:
        return "Erro ao conectar ao banco de dados", 500
    
    cursor = conn.cursor()
    try:
        # Estatísticas de imagens
        cursor.execute('SELECT COUNT(*) FROM image_views')
        total_image_views = cursor.fetchone()[0]
        
        # Estatísticas de boletos
        cursor.execute('SELECT COUNT(*) FROM boleto_views')
        total_boleto_views = cursor.fetchone()[0]
        
        # Visualizações de imagens por fatura
        cursor.execute('''
            SELECT id_fatura, COUNT(*) as views, 
                   MIN(timestamp) as first_view, 
                   MAX(timestamp) as last_view
            FROM image_views 
            GROUP BY id_fatura 
            ORDER BY views DESC
        ''')
        fatura_stats = cursor.fetchall()
        
        # Visualizações de imagens recentes
        cursor.execute('''
            SELECT id_fatura, ip_address, timestamp, user_agent
            FROM image_views 
            ORDER BY timestamp DESC 
            LIMIT 10
        ''')
        recent_image_views = cursor.fetchall()
        
        # Visualizações de boletos por empresa
        cursor.execute('''
            SELECT empresa, COUNT(*) as views, 
                   MIN(timestamp) as first_view, 
                   MAX(timestamp) as last_view
            FROM boleto_views 
            GROUP BY empresa 
            ORDER BY views DESC
        ''')
        boleto_empresa_stats = cursor.fetchall()
        
        # Visualizações de boletos recentes
        cursor.execute('''
            SELECT empresa, codigo_boleto, id_fatura, ip_address, timestamp
            FROM boleto_views 
            ORDER BY timestamp DESC 
            LIMIT 10
        ''')
        recent_boleto_views = cursor.fetchall()
        
        return render_template('dashboard.html', 
                             total_image_views=total_image_views,
                             total_boleto_views=total_boleto_views,
                             fatura_stats=fatura_stats,
                             recent_image_views=recent_image_views,
                             boleto_empresa_stats=boleto_empresa_stats,
                             recent_boleto_views=recent_boleto_views)
    except psycopg2.Error as e:
        print(f"Erro ao buscar estatísticas: {e}")
        return "Erro ao buscar dados do banco", 500
    finally:
        cursor.close()
        conn.close()

@app.route('/image/<filename>')
def serve_image(filename):
    """Serve a imagem com rastreamento de visualizações"""
    id_fatura = request.args.get('id_fatura')
    
    if not id_fatura:
        return "Parâmetro id_fatura é obrigatório", 400
    
    # Registra a visualização
    log_image_view(id_fatura)
    
    # Caminho para a imagem
    image_path = os.path.join(os.getcwd(), filename)
    
    if not os.path.exists(image_path):
        return "Imagem não encontrada", 404
    
    # Retorna a imagem
    return send_file(image_path, mimetype='image/png')

@app.route('/api/stats')
def api_stats():
    """API para obter estatísticas em formato JSON"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Erro ao conectar ao banco de dados'}), 500
    
    cursor = conn.cursor()
    try:
        # Estatísticas de imagens
        cursor.execute('SELECT COUNT(*) FROM image_views')
        total_image_views = cursor.fetchone()[0]
        
        cursor.execute('''
            SELECT id_fatura, COUNT(*) as views
            FROM image_views 
            GROUP BY id_fatura 
            ORDER BY views DESC
        ''')
        fatura_stats = cursor.fetchall()
        
        # Estatísticas de boletos
        cursor.execute('SELECT COUNT(*) FROM boleto_views')
        total_boleto_views = cursor.fetchone()[0]
        
        cursor.execute('''
            SELECT empresa, COUNT(*) as views
            FROM boleto_views 
            GROUP BY empresa 
            ORDER BY views DESC
        ''')
        boleto_stats = cursor.fetchall()
        
        return jsonify({
            'imagens': {
                'total_views': total_image_views,
                'fatura_stats': [{'id_fatura': row[0], 'views': row[1]} for row in fatura_stats]
            },
            'boletos': {
                'total_views': total_boleto_views,
                'empresa_stats': [{'empresa': row[0], 'views': row[1]} for row in boleto_stats]
            }
        })
    except psycopg2.Error as e:
        print(f"Erro ao buscar estatísticas da API: {e}")
        return jsonify({'error': 'Erro ao buscar dados do banco'}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/views/<id_fatura>')
def api_fatura_views(id_fatura):
    """API para obter visualizações de uma fatura específica"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Erro ao conectar ao banco de dados'}), 500
    
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT timestamp, ip_address, user_agent, referer
            FROM image_views 
            WHERE id_fatura = %s
            ORDER BY timestamp DESC
        ''', (id_fatura,))
        
        views = cursor.fetchall()
        
        return jsonify({
            'id_fatura': id_fatura,
            'views': [{
                'timestamp': view[0].isoformat() if view[0] else None,
                'ip_address': view[1],
                'user_agent': view[2],
                'referer': view[3]
            } for view in views]
        })
    except psycopg2.Error as e:
        print(f"Erro ao buscar visualizações da fatura {id_fatura}: {e}")
        return jsonify({'error': 'Erro ao buscar dados do banco'}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/boleto')
def redirect_boleto():
    """Redireciona para o boleto baseado na empresa e código"""
    empresa = request.args.get('empresa', '').lower()
    codigo = request.args.get('codigo', '')
    id_fatura = request.args.get('id_fatura', '')  # Parâmetro opcional
    
    # Validação dos parâmetros obrigatórios
    if not empresa or not codigo:
        return jsonify({
            'error': 'Parâmetros obrigatórios: empresa e codigo',
            'parametros_opcionais': ['id_fatura'],
            'exemplo': '/boleto?empresa=megalink&codigo=c42f66f6bc19678efa2a983f93170cb31ed23d0c6e1cefe03f72fe62cf5ea9b21f71e4e61850ef5c&id_fatura=FAT001'
        }), 400
    
    # Mapeamento das empresas para suas URLs base
    empresas_urls = {
        'megalink': 'https://api.megalinktelecom.hubsoft.com.br/pdf/fatura/',
        'bjfibra': 'https://api.bjfibra.hubsoft.com.br/pdf/fatura/'
    }
    
    # Verifica se a empresa é válida
    if empresa not in empresas_urls:
        return jsonify({
            'error': 'Empresa inválida',
            'empresas_validas': list(empresas_urls.keys())
        }), 400
    
    # Constrói a URL completa do boleto
    url_boleto = empresas_urls[empresa] + codigo
    
    # Registra o acesso ao boleto na tabela específica
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO boleto_views (empresa, codigo_boleto, id_fatura, ip_address, user_agent, referer)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (
                empresa,
                codigo,
                id_fatura if id_fatura else None,  # id_fatura é opcional
                request.remote_addr,
                request.headers.get('User-Agent', ''),
                request.headers.get('Referer', '')
            ))
            conn.commit()
            cursor.close()
            conn.close()
            print(f"Acesso ao boleto registrado: {empresa} - {codigo[:8]} - Fatura: {id_fatura or 'N/A'}")
    except Exception as e:
        print(f"Erro ao registrar acesso ao boleto: {e}")
    
    # Redireciona para o boleto
    return redirect(url_boleto, code=302)

@app.route('/api/empresas')
def api_empresas():
    """API para listar empresas disponíveis e suas URLs base"""
    empresas_info = {
        'megalink': {
            'nome': 'Megalink Telecom',
            'url_base': 'https://api.megalinktelecom.hubsoft.com.br/pdf/fatura/',
            'exemplo': '/boleto?empresa=megalink&codigo=c42f66f6bc19678efa2a983f93170cb31ed23d0c6e1cefe03f72fe62cf5ea9b21f71e4e61850ef5c'
        },
        'bjfibra': {
            'nome': 'BJ Fibra',
            'url_base': 'https://api.bjfibra.hubsoft.com.br/pdf/fatura/',
            'exemplo': '/boleto?empresa=bjfibra&codigo=c42f66f6bc19678efa2a983f93170cb31ed23d0c6e1cefe03f72fe62cf5ea9b21f71e4e61850ef5c'
        }
    }
    
    return jsonify({
        'empresas': empresas_info,
        'instrucoes': {
            'rota': '/boleto',
            'parametros_obrigatorios': ['empresa', 'codigo'],
            'parametros_opcionais': ['id_fatura'],
            'formato_url': '/boleto?empresa={empresa}&codigo={codigo_boleto}&id_fatura={id_fatura}',
            'exemplo_uso': 'https://seudominio.com/boleto?empresa=megalink&codigo=c42f66f6bc19678efa2a983f93170cb31ed23d0c6e1cefe03f72fe62cf5ea9b21f71e4e61850ef5c&id_fatura=FAT001'
        }
    })

@app.route('/api/boletos/<empresa>')
def api_empresa_boletos(empresa):
    """API para obter visualizações de boletos de uma empresa específica"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Erro ao conectar ao banco de dados'}), 500
    
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT codigo_boleto, id_fatura, ip_address, timestamp, user_agent
            FROM boleto_views 
            WHERE empresa = %s
            ORDER BY timestamp DESC
        ''', (empresa,))
        
        boletos = cursor.fetchall()
        
        return jsonify({
            'empresa': empresa,
            'total_boletos': len(boletos),
            'boletos': [{
                'codigo_boleto': boleto[0],
                'id_fatura': boleto[1],
                'ip_address': boleto[2],
                'timestamp': boleto[3].isoformat() if boleto[3] else None,
                'user_agent': boleto[4]
            } for boleto in boletos]
        })
    except psycopg2.Error as e:
        print(f"Erro ao buscar boletos da empresa {empresa}: {e}")
        return jsonify({'error': 'Erro ao buscar dados do banco'}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    init_db()
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)