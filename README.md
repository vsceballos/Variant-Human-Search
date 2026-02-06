# Variant-Human-Search

Flask-based API for querying human genetic variants (SNPs) via Ensembl REST and VEP, returning standardized JSON output.

**Status**: ✅ Production Ready

## Descrição

Esta aplicação é uma **API web** desenvolvida em Python utilizando **Flask**, que permite a consulta de variantes genéticas humanas (SNPs) a partir de um rsID (ex: rs699).

A aplicação consome a **API REST do Ensembl** para obter informações da variante e utiliza o endpoint **VEP** (Variant Effect Predictor) para identificar genes associados e a consequência biológica mais relevante.

O resultado é retornado em um **JSON padronizado**, com tratamento de erros robusto e valores ausentes devidamente representados.

## 🌟 Funcionalidades

- ✅ Consulta de variantes humanas via rsID
- ✅ Integração com Ensembl REST API
- ✅ Integração com Ensembl VEP para anotação funcional
- ✅ Retorno de JSON padronizado
- ✅ Tratamento robusto de erros (rsID inválido, variante inexistente, timeouts, falhas de conexão)
- ✅ Cache em memória (últimas 50 pesquisas) para otimização
- ✅ Interface web intuitiva (HTML5 + Bootstrap)
- ✅ Endpoint REST para consumo por outras aplicações
- ✅ Logging estruturado para debug em produção
- ✅ CORS habilitado para integração cross-domain
- ✅ Cobertura de testes com pytest

## 📦 Estrutura do Projeto

```
Variant-Human-Search/
├── variant_app.py           # Backend (Flask + Lógica de API)
├── test_app.py              # Testes unitários (Pytest com Mocks)
├── requirements.txt         # Dependências Python
├── Dockerfile               # Container Docker (segurança otimizada)
├── .env.example             # Variáveis de ambiente (template)
├── README.md                # Documentação
└── templates/
    └── index.html           # Interface Web (HTML5 + Bootstrap)
```

## 📋 Requisitos

- **Python 3.8+**
- Bibliotecas Python (ver `requirements.txt`):
  - Flask 3.0.0
  - Flask-CORS 4.0.0
  - requests 2.31.0+
  - python-dotenv 1.0.0
  - pytest 7.4.0

### Conectividade
- Acesso à internet para consumir APIs do Ensembl

## 🚀 Instalação e Setup

### Opção 1: Executar Localmente

1. **Clone ou copie o projeto**
```bash
git clone https://github.com/vsceballos/Variant-Human-Search/
cd Variant-Human-Search
```

2. **Crie um ambiente virtual** (recomendado)
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

3. **Instale as dependências**
```bash
pip install -r requirements.txt
```

4. **(Opcional) Configure as variáveis de ambiente**
```bash
cp .env.example .env
# Edite .env se desejar customizar configurações
```

5. **Execute a aplicação**
```bash
python variant_app.py
```

A aplicação abrirá automaticamente em `http://127.0.0.1:5000`
#Caso não abra, acesse manualmente.

### Opção 2: Executar com Docker

```bash
# Build da imagem
docker build -t variant-search .

# Executar o container
docker run -p 5000:5000 -e FLASK_DEBUG=False variant-search

# Com variáveis de ambiente customizadas
docker run -p 5000:5000 \
  -e REQUEST_TIMEOUT=15 \
  -e LOG_LEVEL=DEBUG \
  variant-search
```

## 🔌 Como Usar

### Via Interface Web

1. Acesse `http://localhost:5000`
2. Digite um rsID válido (ex: `rs1333049` ou `rs699`)
3. Clique em "Buscar Variante"
4. Visualize os resultados em uma tabela formatada

### Via API REST

#### Endpoint: `GET /api/search/<rsid>`

**Exemplo de Requisição:**
```bash
curl -X GET "http://localhost:5000/api/search/rs1333049"
```

**Resposta de Sucesso (200):**
```json
{
  "rsid": "rs1333049",
  "chromosome": "9",
  "position": 22125504,
  "alleles": "C/G",
  "minor_allele_freq": 0.4473,
  "genes": ["CDKN2B"],
  "consequence": "intergenic_variant"
}
```

**Resposta - Variante Não Encontrada (404):**
```json
{
  "error": "Variante não encontrada no Ensembl."
}
```

**Resposta - Formato Inválido (400):**
```json
{
  "error": "Formato inválido. Use 'rs' seguido de números."
}
```

**Resposta - Timeout (504):**
```json
{
  "error": "Timeout: requisição levou mais de 10 segundos"
}
```

## 📊 Formato do JSON de Saída

```json
{
  "rsid": "string",              // ID da variante (ex: rs1333049)
  "chromosome": "string",        // Cromossomo (ex: "9")
  "position": "integer",         // Posição em pares de bases
  "alleles": "string",           // Alelos separados por / (ex: "C/G")
  "minor_allele_freq": "float",  // Frequência do alelo menor (0-1)
  "genes": ["string"],           // Lista de genes associados
  "consequence": "string"        // Consequência biológica mais severa
}
```

**Nota:** Nem todos os campos estão disponíveis para todas as variantes. Quando ausentes, os valores são retornados como `null` ou listas vazias.

## ⚙️ Variáveis de Ambiente

Crie um arquivo `.env` baseado em `.env.example`:

```env
# Configuração do Flask
FLASK_DEBUG=False              # True apenas em desenvolvimento
FLASK_HOST=0.0.0.0             # Host para bind
FLASK_PORT=5000                # Porta da aplicação

# URLs da API Ensembl
ENSEMBL_VARIANT_URL=https://rest.ensembl.org/variation/human/
ENSEMBL_VEP_URL=https://rest.ensembl.org/vep/human/id/

# Timeout para requisições externas (segundos)
REQUEST_TIMEOUT=10

# Nível de logging
LOG_LEVEL=INFO                 # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Comportamento de inicialização
OPEN_BROWSER=False             # Não abrir navegador em produção
```

## 🧪 Testes

Execute os testes unitários com pytest:

```bash
# Rodar todos os testes
pytest test_app.py -v

# Executar testes com coverage
pytest test_app.py --cov=variant_app --cov-report=html

# Testes específicos
pytest test_app.py::test_api_search_success -v
```

### Cobertura de Testes

Testes incluídos:
- ✅ Página inicial carrega corretamente
- ✅ Busca de variante bem-sucedida (Form)
- ✅ Variante não encontrada
- ✅ API endpoint com sucesso
- ✅ API endpoint variante não encontrada
- ✅ API endpoint formato inválido
- ✅ API endpoint com timeout
- ✅ Formulário com rsID vazio

## 🔧 Desenvolvimento

### Debug Local

Para ativar mode debug com logging detalhado:

```bash
export FLASK_DEBUG=True
export LOG_LEVEL=DEBUG
export OPEN_BROWSER=True
python variant_app.py
```

### Adicionar Cache Redis (Opcional)

Para cache persistente entre execuções, substitua `@lru_cache` por Redis no `variant_app.py`.

### Limitação de Taxa (Rate Limiting)

Para adicionar proteção contra abuso, instale e configure `Flask-Limiter`:

```bash
pip install Flask-Limiter
```

## 🐳 Docker

### Build e Push para Registry

```bash
# Build
docker build -t seu-usuario/variant-search:1.0 .

# Push para Docker Hub
docker push seu-usuario/variant-search:1.0

# Executar
docker run -p 5000:5000 seu-usuario/variant-search:1.0
```

### Health Check

O container inclui health check automático (a cada 30s com 3 retries).

Verificar status:
```bash
docker ps --format "table {{.Names}}\t{{.Status}}"
```

## 📝 Logging

Logs são exibidos no console:

```
2025-02-06 10:30:45,123 - variant_app - INFO - Buscando variante: rs1333049
2025-02-06 10:30:46,456 - variant_app - INFO - Variante rs1333049 encontrada com sucesso
```

Configure o nível com `LOG_LEVEL`:
- `DEBUG`: Informações detalhadas
- `INFO`: Informações gerais
- `WARNING`: Avisos
- `ERROR`: Erros
- `CRITICAL`: Problemas críticos

## 🛡️ Segurança

✅ **Implementado:**
- Validação de entrada (rsID format)
- Timeouts em requisições externas
- Usuário não-root em Docker
- CORS configurado
- Variáveis de ambiente para dados sensíveis

⚠️ **Recomendações para Produção:**
- Usar HTTPS/TLS
- Implementar autenticação (API Key ou OAuth)
- Adicionar rate limiting
- Usar load balancer (nginx/apache)
- Monitoramento com Prometheus/Grafana
- Logs centralizados (ELK Stack)


## 👤 Autor

**Victor Ceballos**
**Bioinformata**
## 🔗 Links Úteis

- [Ensembl REST API](https://rest.ensembl.org)
- [Variant Effect Predictor (VEP)](https://rest.ensembl.org/documentation/info/vep_id_post)
- [Flask Documentation](https://flask.palletsprojects.com)
- [Python Requests](https://docs.python-requests.org)

