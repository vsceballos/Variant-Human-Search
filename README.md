# Variant-Human-Search
Flask-based API for querying human genetic variants (SNPs) via Ensembl REST and VEP, returning standardized JSON output.

Variant Human Search - SNP
==============================

Estrutura do projeto

├── variant_app.py      # Aplicação Backend (Flask + Lógica de API)

├── Dockerfile          # Receita de container (Segurança aplicada)

├── requirements.txt    # Lista de dependências Python

├── test_app.py         # Testes unitários (Pytest com Mocks)

├── README.md           # Documentação do projeto

└── templates/

    └── index.html      # Interface Frontend (HTML5 + Bootstrap)

Descrição
---------
Esta aplicação é uma API web desenvolvida em Python utilizando Flask,
que permite a consulta de variantes genéticas humanas (SNPs) a partir de um rsID
(ex: rs699).

A aplicação consome a API REST do Ensembl para obter informações da variante e
utiliza o endpoint VEP (Variant Effect Predictor) para identificar genes
associados e a consequência biológica mais relevante.

O resultado é retornado em um JSON padronizado,
com tratamento de erros e valores ausentes.


Funcionalidades
---------------
- Consulta de variantes humanas via rsID
- Integração com Ensembl REST API
- Integração com Ensembl VEP para anotação funcional
- Retorno de JSON padronizado
- Tratamento de erros (rsID inválido, variante inexistente, falhas de conexão)
- Cache em memória para otimização de requisições repetidas
- Interface web simples para uso manual
- Endpoint REST para consumo por outras aplicações


Formato do JSON de Saída
------------------------
{

  "rsid": "",
  
  "chromosome": "",
  
  "position": null,

  "alleles": "",
  
  "minor_allele_freq": null,
  
  "genes": [],
  
  "consequence": ""
  
}

Obs: Nem todos os campos estão disponíveis para todas as variantes.
Quando ausentes, os valores são retornados como null ou listas vazias.


Requisitos
----------
- Python 3.8 ou superior
- Bibliotecas Python:
  - Flask
  - requests


Rodar Localmente:
----------
1. Clone ou copie o projeto
2. Instale as dependências:

    pip install -r requirements.txt


Execução
--------
Para iniciar a aplicação:

Primeiro você deverá dar permissão de execução do arquivo py com o seguinte comando

    chmod +x variant_app.py 

Feito isso você deverá executar o comando

    ./variant_app.py

A aplicação será iniciada localmente em:
   http://127.0.0.1:5000


Opção 2: Rodar via Docker
--------------------

Para um ambiente isolado e reprodutível:

Construa a imagem:

    docker build -t bioinfo-app .
    
OU 

    sudo docker build --network=host -t bioinfo-app .

Ambos os comandos devem rodar sem aspas.

Inicie o container:

    docker run -p 5000:5000 bioinfo-app
    
OU 

    sudo docker run --network=host bioinfo-app


Abra seu navegador e acesse: # http://localhost:5000


Uso via API REST
----------------
Endpoint:

   Com o aplicativo rodando através do docker em outra aba digite o seguinte exemplo:
   
Exemplo:

    curl http://localhost:5000/api/search/rs1801133

Resposta:
JSON padronizado com informações da variante.


Tratamento de Erros
-------------------
- rsID inválido: retorna erro 400
- Variante não encontrada: retorna erro 404
- Falha de comunicação com a API externa: retorna erro 500


Autor
-----
Victor Ceballos - Bioinformata
