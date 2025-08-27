# 📧 Sistema de Rastreamento de Imagens em E-mails

Este sistema permite rastrear quando e por quem suas imagens em e-mails são visualizadas, capturando informações como ID da fatura, IP do cliente, data/hora e outros metadados.

## 🚀 Funcionalidades

- **Rastreamento de Visualizações**: Captura cada vez que uma imagem é carregada
- **Dashboard em Tempo Real**: Interface web para monitorar estatísticas
- **APIs REST**: Endpoints para integração com outros sistemas
- **Banco de Dados SQLite**: Armazenamento local das visualizações
- **Interface Responsiva**: Dashboard moderno e adaptável a dispositivos móveis

## 📋 Pré-requisitos

- Python 3.7+
- pip (gerenciador de pacotes Python)
- Acesso ao banco PostgreSQL (configurado em config.py)

## 🛠️ Instalação

1. **Clone ou baixe os arquivos** para seu servidor
2. **Instale as dependências**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Execute a aplicação**:
   ```bash
   python app.py
   ```

A aplicação estará disponível em `http://localhost:5001`

## 📖 Como Usar

### 1. Configuração no Template de E-mail

Para rastrear visualizações, adicione a seguinte URL no seu template de e-mail:

```html
<img src="http://seu-dominio:5001/image/img1.png?id_fatura=ID_DA_FATURA" alt="Imagem">
```

**Exemplo prático:**
```html
<img src="http://meuservidor.com:5001/image/img1.png?id_fatura=FAT001" alt="Logo da Empresa">
```

### 2. Parâmetros Obrigatórios

- **id_fatura**: Identificador único da fatura (obrigatório)
- **filename**: Nome do arquivo de imagem (ex: img1.png)

### 3. Acessando o Dashboard

Acesse `http://seu-dominio:5001` para ver:
- Total de visualizações
- Estatísticas por fatura
- Visualizações recentes
- Histórico completo

## 🔗 APIs Disponíveis

### Estatísticas Gerais
```
GET /api/stats
```
Retorna estatísticas gerais em formato JSON.

### Visualizações de uma Fatura Específica
```
GET /api/views/{id_fatura}
```
Retorna todas as visualizações de uma fatura específica.

## 📊 Dados Capturados

Para cada visualização, o sistema registra:
- **ID da Fatura**: Identificador único da fatura
- **Endereço IP**: IP do cliente que visualizou
- **User Agent**: Navegador/dispositivo usado
- **Referer**: Página de origem (se disponível)
- **Timestamp**: Data e hora exata da visualização

## 🗄️ Estrutura do Banco de Dados

O sistema usa PostgreSQL com a seguinte estrutura:

```sql
CREATE TABLE image_views (
    id SERIAL PRIMARY KEY,
    id_fatura VARCHAR(255) NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    referer TEXT
);
```

## 🔧 Configuração

### Alterando a Porta
Edite o arquivo `app.py` e modifique a linha:
```python
app.run(host="0.0.0.0", port=5001, debug=True)
```

### Alterando o Host
Para aceitar conexões externas, mantenha `host="0.0.0.0"`
Para apenas conexões locais, use `host="127.0.0.1"`

## 📁 Estrutura de Arquivos

```
megalink_emails/
├── app.py              # Aplicação Flask principal
├── config.py           # Configurações da aplicação
├── requirements.txt    # Dependências Python
├── README.md          # Este arquivo
├── img1.png           # Imagem de exemplo
├── templates/         # Templates HTML
│   └── dashboard.html # Dashboard principal
└── start.sh           # Script de inicialização
```

## 🚨 Segurança

- **Firewall**: Configure seu firewall para permitir apenas conexões necessárias
- **HTTPS**: Em produção, use HTTPS para proteger os dados
- **Autenticação**: Considere adicionar autenticação para o dashboard
- **Rate Limiting**: Implemente limitação de taxa para evitar abuso

## 🔍 Monitoramento

### Logs da Aplicação
A aplicação Flask gera logs automáticos. Monitore:
- Acesso às imagens
- Erros de banco de dados
- Tentativas de acesso inválido

### Métricas Importantes
- **Taxa de Abertura**: Visualizações únicas por fatura
- **Horários de Pico**: Quando as imagens são mais visualizadas
- **Dispositivos**: Tipos de dispositivos usados pelos clientes

## 🆘 Suporte

Para problemas ou dúvidas:
1. Verifique os logs da aplicação
2. Confirme se o banco de dados foi criado
3. Teste a conectividade da rede
4. Verifique as permissões de arquivo

## 📈 Exemplos de Uso

### E-mail de Cobrança
```html
<p>Olá, sua fatura está em anexo.</p>
<img src="http://servidor.com:5001/image/logo.png?id_fatura=FAT2024001" alt="Logo">
<p>Obrigado pela preferência!</p>
```

### Newsletter
```html
<h1>Nossa Newsletter</h1>
<img src="http://servidor.com:5001/image/banner.png?id_fatura=NEWS001" alt="Banner">
<p>Conteúdo da newsletter...</p>
```

## 🔄 Atualizações

O dashboard atualiza automaticamente a cada 30 segundos. Use o botão "🔄 Atualizar" para atualizações manuais.
