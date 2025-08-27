from flask import Flask, send_file, request, render_template, jsonify
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
    """Inicializa o banco de dados com a tabela necessária"""
    conn = get_db_connection()
    if not conn:
        print("Não foi possível conectar ao banco de dados")
        return
    
    cursor = conn.cursor()
    try:
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
        conn.commit()
        print("Tabela image_views criada/verificada com sucesso!")
    except psycopg2.Error as e:
        print(f"Erro ao criar tabela: {e}")
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
        # Total de visualizações
        cursor.execute('SELECT COUNT(*) FROM image_views')
        total_views = cursor.fetchone()[0]
        
        # Visualizações por fatura
        cursor.execute('''
            SELECT id_fatura, COUNT(*) as views, 
                   MIN(timestamp) as first_view, 
                   MAX(timestamp) as last_view
            FROM image_views 
            GROUP BY id_fatura 
            ORDER BY views DESC
        ''')
        fatura_stats = cursor.fetchall()
        
        # Visualizações recentes
        cursor.execute('''
            SELECT id_fatura, ip_address, timestamp, user_agent
            FROM image_views 
            ORDER BY timestamp DESC 
            LIMIT 10
        ''')
        recent_views = cursor.fetchall()
        
        return render_template('dashboard.html', 
                             total_views=total_views,
                             fatura_stats=fatura_stats,
                             recent_views=recent_views)
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
        cursor.execute('SELECT COUNT(*) FROM image_views')
        total_views = cursor.fetchone()[0]
        
        cursor.execute('''
            SELECT id_fatura, COUNT(*) as views
            FROM image_views 
            GROUP BY id_fatura 
            ORDER BY views DESC
        ''')
        fatura_stats = cursor.fetchall()
        
        return jsonify({
            'total_views': total_views,
            'fatura_stats': [{'id_fatura': row[0], 'views': row[1]} for row in fatura_stats]
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

if __name__ == "__main__":
    init_db()
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)