#!/usr/bin/env python3

import os
import re
import logging
import requests
import webbrowser
from threading import Timer
from functools import lru_cache
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configurar logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

ENSEMBL_VARIANT_URL = os.getenv('ENSEMBL_VARIANT_URL', 'https://rest.ensembl.org/variation/human/')
ENSEMBL_VEP_URL = os.getenv('ENSEMBL_VEP_URL', 'https://rest.ensembl.org/vep/human/id/')
REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '10'))

HEADERS = {"Content-Type": "application/json"}

# O cache irá guardar as 50 ultimas pesquisas realizadas pelo usuário
@lru_cache(maxsize=50)
def fetch_variant_data(rsid):
    """
    Busca informações de uma variante no Ensembl e normaliza a saída
    conforme o padrão solicitado no desafio.
    """
    try:
        logger.info(f"Buscando variante: {rsid}")
        
        # Consulta principal da variante
        response_var = requests.get(
            f"{ENSEMBL_VARIANT_URL}{rsid}", 
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT
        )

        if response_var.status_code == 404:
            logger.warning(f"Variante não encontrada: {rsid}")
            return None, "Variante não encontrada no Ensembl."
        if response_var.status_code != 200:
            logger.error(f"Erro API Variantes (status {response_var.status_code}): {rsid}")
            return None, f"Erro ao consultar Ensembl (status {response_var.status_code})"

        data = response_var.json()
        mapping = data.get("mappings", [{}])[0]

        # Consulta VEP para identificar genes associados
        response_vep = requests.get(
            f"{ENSEMBL_VEP_URL}{rsid}", 
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT
        )

        gene_names = set()

        if response_vep.status_code == 200:
            vep_data = response_vep.json()
            for item in vep_data:
                for transcript in item.get("transcript_consequences", []):
                    gene_symbol = transcript.get("gene_symbol")
                    if gene_symbol:
                        gene_names.add(gene_symbol)
        elif response_vep.status_code != 404:
            logger.warning(f"VEP retornou status {response_vep.status_code} para {rsid}")
        
        # Formata a lista de genes
        formatted_data = {
            "rsid": data.get("name", rsid),
            "chromosome": mapping.get("seq_region_name"),
            "position": mapping.get("start"),
            "alleles": mapping.get("allele_string"),
            "minor_allele_freq": data.get("MAF"),
            "genes": sorted(gene_names),
            "consequence": data.get("most_severe_consequence"),
        }

        logger.info(f"Variante {rsid} encontrada com sucesso")
        return formatted_data, None

    except requests.Timeout:
        logger.error(f"Timeout ao buscar {rsid} após {REQUEST_TIMEOUT}s")
        return None, f"Timeout: requisição levou mais de {REQUEST_TIMEOUT} segundos"
    except requests.RequestException as e:
        logger.error(f"Erro de conexão ao buscar {rsid}: {str(e)}")
        return None, f"Erro de conexão com o Ensembl. Tente novamente mais tarde."


def open_browser():
    """Abre o navegador automaticamente ao iniciar a aplicação."""
    try:
        webbrowser.open_new("http://127.0.0.1:5000")
        logger.info("Navegador aberto automaticamente")
    except Exception as e:
        logger.warning(f"Não foi possível abrir o navegador automaticamente: {e}")


@app.route("/", methods=["GET", "POST"])
def index():
    variant_info = None
    error_message = None

    if request.method == "POST":
        rsid = request.form.get("rsid", "").strip()
        
        # Verifica se começa com 'rs' seguido de números
        if not rsid:
            error_message = "Por favor, insira um rsID."
        elif not re.match(r"^rs\d+$", rsid):
            error_message = (
                "Formato inválido! Use 'rs' seguido de números (ex: rs1333049)."
            )
        else:
            logger.debug(f"Buscando variante via formulário: {rsid}")
            variant_info, error_message = fetch_variant_data(rsid)

    return render_template(
        "index.html", info=variant_info, error=error_message
    )


@app.route("/api/search/<rsid>", methods=["GET"])
def api_search(rsid):
    """API endpoint para buscar variantes geneticamente."""
    if not re.match(r"^rs\d+$", rsid):
        logger.warning(f"Formato inválido na API: {rsid}")
        return jsonify({"error": "Formato inválido. Use 'rs' seguido de números."}), 400

    logger.info(f"Requisição da API para: {rsid}")
    data, error = fetch_variant_data(rsid)

    if error:
        if "não encontrada" in error.lower():
            return jsonify({"error": error}), 404
        elif "timeout" in error.lower():
            return jsonify({"error": error}), 504
        else:
            return jsonify({"error": error}), 500

    return jsonify(data)


if __name__ == "__main__":
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    open_browser_on_start = os.getenv('OPEN_BROWSER', 'True').lower() == 'true'
    
    if debug_mode and open_browser_on_start and (not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true"):
        Timer(1, open_browser).start()
    
    logger.info(f"Iniciando aplicação (debug={debug_mode})")
    app.run(
        host=os.getenv('FLASK_HOST', '0.0.0.0'),
        port=int(os.getenv('FLASK_PORT', '5000')),
        debug=debug_mode
    )

