# Configurações da aplicação Flask para rastreamento de imagens

import os

class Config:
    """Configurações padrão da aplicação"""
    
    # Configurações do servidor
    HOST = "0.0.0.0"  # Aceita conexões externas
    PORT = 5001
    DEBUG = True
    
    # Configurações do banco de dados PostgreSQL
    DATABASE_CONFIG = {
        'ENGINE': 'postgresql',
        'NAME': 'megalink_email',
        'USER': 'admin',
        'PASSWORD': 'qualidade@trunks.57',
        'HOST': '187.62.153.52',
        'PORT': '5432',
    }
    
    # String de conexão PostgreSQL
    DATABASE_URL = f"postgresql://{DATABASE_CONFIG['USER']}:{DATABASE_CONFIG['PASSWORD']}@{DATABASE_CONFIG['HOST']}:{DATABASE_CONFIG['PORT']}/{DATABASE_CONFIG['NAME']}"
    
    # Configurações de segurança
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Configurações de logging
    LOG_LEVEL = 'INFO'
    
    # Configurações de cache
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutos
    
    # Configurações de rate limiting
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URL = 'memory://'
    
    # Configurações de CORS (se necessário)
    CORS_ORIGINS = ['*']  # Em produção, especifique domínios específicos

class DevelopmentConfig(Config):
    """Configurações para desenvolvimento"""
    DEBUG = True
    # Usa o mesmo banco PostgreSQL em desenvolvimento

class ProductionConfig(Config):
    """Configurações para produção"""
    DEBUG = False
    HOST = "0.0.0.0"
    PORT = 5001
    # Usa o mesmo banco PostgreSQL em produção
    
    # Em produção, desabilite CORS amplo
    CORS_ORIGINS = [
        'https://seudominio.com',
        'https://www.seudominio.com'
    ]

class TestingConfig(Config):
    """Configurações para testes"""
    TESTING = True
    DEBUG = True
    # Para testes, você pode criar um banco separado se necessário

# Configuração baseada em variável de ambiente
def get_config():
    """Retorna a configuração baseada na variável de ambiente FLASK_ENV"""
    env = os.environ.get('FLASK_ENV', 'development')
    
    if env == 'production':
        return ProductionConfig
    elif env == 'testing':
        return TestingConfig
    else:
        return DevelopmentConfig

# Configuração atual
config = get_config()
