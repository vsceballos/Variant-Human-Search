import pytest
from variant_app import app, fetch_variant_data
from unittest.mock import patch

@pytest.fixture
def client():
    app.config['TESTING'] = True
    # Patch no Timer para evitar abrir navegador durante testes
    with patch('variant_app.Timer'): 
        with app.test_client() as client:
            yield client

def test_home_page(client):
    """Testa se a página inicial carrega corretamente."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Human Variant Search - SNP" in response.data or b"Human" in response.data

@patch('variant_app.requests.get')
def test_search_variant_success(mock_get, client):
    """Testa uma busca bem-sucedida simulando a resposta da API."""
    
    # 0. Limpa o cache para garantir um teste fresco
    fetch_variant_data.cache_clear()
    
    # 1. Simula a resposta do Endpoint da Variante
    mock_response_var = {
        "name": "rs123",
        "mappings": [{"seq_region_name": "1", "start": 1000, "allele_string": "A/G"}],
        "most_severe_consequence": "missense_variant",
        "MAF": 0.05
    }
    
    # 2. Simula a resposta do Endpoint do VEP (Gene)
    mock_response_vep = [
        {"transcript_consequences": [{"gene_symbol": "TEST-GENE"}]}
    ]

    # Configura o mock para devolver essas respostas em sequência
    mock_get.side_effect = [
        type('obj', (object,), {'status_code': 200, 'json': lambda: mock_response_var}),
        type('obj', (object,), {'status_code': 200, 'json': lambda: mock_response_vep})
    ]

    # Envia o POST
    response = client.post('/', data={'rsid': 'rs123'})
    
    assert response.status_code == 200
    assert b"rs123" in response.data
    assert b"TEST-GENE" in response.data

@patch('variant_app.requests.get')
def test_search_variant_not_found(mock_get, client):
    """Testa o comportamento quando o rsID não existe."""
    
    # 0. Limpa o cache
    fetch_variant_data.cache_clear()

    # 1. Configura a Internet Falsa para devolver Erro 404
    mock_get.return_value.status_code = 404
    
    # 2. Faz a busca
    response = client.post('/', data={'rsid': 'rs00000'})
    
    # 3. Verifica se a aplicação lidou bem com o erro
    assert response.status_code == 200
    # Procura por partes da frase "Variante não encontrada"
    # O 'b' antes da string significa bytes (padrão do Flask testing)
    assert b"Variante n" in response.data or b"nao encontrada" in response.data

# Testes da API REST

@patch('variant_app.requests.get')
def test_api_search_success(mock_get, client):
    """Testa requisição bem-sucedida ao endpoint da API."""
    fetch_variant_data.cache_clear()
    
    mock_response_var = {
        "name": "rs456",
        "mappings": [{"seq_region_name": "2", "start": 2000, "allele_string": "C/T"}],
        "most_severe_consequence": "synonymous_variant",
        "MAF": 0.10
    }
    
    mock_response_vep = [
        {"transcript_consequences": [{"gene_symbol": "API-GENE"}]}
    ]

    mock_get.side_effect = [
        type('obj', (object,), {'status_code': 200, 'json': lambda: mock_response_var}),
        type('obj', (object,), {'status_code': 200, 'json': lambda: mock_response_vep})
    ]

    response = client.get('/api/search/rs456')
    
    assert response.status_code == 200
    import json
    data = json.loads(response.data)
    assert data['rsid'] == 'rs456'
    assert data['chromosome'] == '2'
    assert 'API-GENE' in data['genes']

@patch('variant_app.requests.get')
def test_api_search_not_found(mock_get, client):
    """Testa requisição da API quando variante não existe."""
    fetch_variant_data.cache_clear()
    
    mock_get.return_value.status_code = 404
    
    response = client.get('/api/search/rs99999')
    
    assert response.status_code == 404
    import json
    data = json.loads(response.data)
    assert 'error' in data

def test_api_search_invalid_format(client):
    """Testa requisição da API com formato inválido."""
    response = client.get('/api/search/invalid')
    
    assert response.status_code == 400
    import json
    data = json.loads(response.data)
    assert 'error' in data
    assert 'Formato' in data['error']

@patch('variant_app.requests.get')
def test_api_search_timeout(mock_get, client):
    """Testa requisição da API com timeout."""
    fetch_variant_data.cache_clear()
    
    import requests
    mock_get.side_effect = requests.Timeout("Connection timeout")
    
    response = client.get('/api/search/rs789')
    
    assert response.status_code == 504
    import json
    data = json.loads(response.data)
    assert 'error' in data
    assert 'Timeout' in data['error']

def test_form_empty_rsid(client):
    """Testa formulário com rsID vazio."""
    response = client.post('/', data={'rsid': ''})
    
    assert response.status_code == 200
    assert b'Por favor' in response.data or b'insira' in response.data
