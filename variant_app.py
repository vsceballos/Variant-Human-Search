#!/usr/bin/env python3

import os
import re
import requests
import webbrowser
from threading import Timer
from functools import lru_cache
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

ENSEMBL_VARIANT_URL = "https://rest.ensembl.org/variation/human/"
ENSEMBL_VEP_URL = "https://rest.ensembl.org/vep/human/id/"

HEADERS = {"Content-Type": "application/json"}

# O cache irá guardar as 50 ultimas pesquisas realizadas pelo usuário
@lru_cache(maxsize=50)
def fetch_variant_data(rsid):
    """
    Busca informações de uma variante no Ensembl e normaliza a saída
    conforme o padrão solicitado no desafio.
    """
    try:
        #Consulta principal da variante
        response_var = requests.get(
            f"{ENSEMBL_VARIANT_URL}{rsid}", headers=HEADERS
        )

        if response_var.status_code == 404:
            return None, "Variante não encontrada no Ensembl."
        if response_var.status_code != 200:
            return None, f"Erro API Variantes: {response_var.status_code}"

        data = response_var.json()
        mapping = data.get("mappings", [{}])[0]

        #Consulta VEP para identificar genes associados
        response_vep = requests.get(
            f"{ENSEMBL_VEP_URL}{rsid}", headers=HEADERS
        )

        gene_names = set()

        if response_vep.status_code == 200:
            vep_data = response_vep.json()
            for item in vep_data:
                for transcript in item.get("transcript_consequences", []):
                    gene_symbol = transcript.get("gene_symbol")
                    if gene_symbol:
                        gene_names.add(gene_symbol)
        
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

        return formatted_data, None

    except requests.RequestException as e:
        return None, f"Erro de conexão: {str(e)}"


def open_browser():
    """Abre o navegador automaticamente ao iniciar a aplicação."""
    webbrowser.open_new("http://127.0.0.1:5000")


@app.route("/", methods=["GET", "POST"])
def index():
    variant_info = None
    error_message = None

    if request.method == "POST":
        rsid = request.form.get("rsid", "").strip()
        
        # Verifica se começa com 'rs' seguido de números
        if not re.match(r"^rs\d+$", rsid):
            error_message = (
                "Formato inválido! Use 'rs' seguido de números (ex: rs1333049)."
            )
        else:
            variant_info, error_message = fetch_variant_data(rsid)

    return render_template(
        "index.html", info=variant_info, error=error_message
    )


@app.route("/api/search/<rsid>", methods=["GET"])
def api_search(rsid):
    if not re.match(r"^rs\d+$", rsid):
        return jsonify({"error": "Formato inválido"}), 400

    data, error = fetch_variant_data(rsid)

    if error:
        status = 404 if "não encontrada" in error.lower() else 500
        return jsonify({"error": error}), status

    return jsonify(data)


if __name__ == "__main__":
    if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        Timer(1, open_browser).start()

    app.run(host="0.0.0.0", port=5000, debug=True)

