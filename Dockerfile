# Usa uma imagem oficial leve do Python (Linux Debian-based)
FROM python:3.9-slim

# Define diretório de trabalho no container
WORKDIR /app

# Define variáveis de ambiente padrão
ENV FLASK_APP=variant_app.py \
    FLASK_ENV=production \
    FLASK_DEBUG=False \
    OPEN_BROWSER=False \
    REQUEST_TIMEOUT=10 \
    LOG_LEVEL=INFO \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Copia os arquivos de dependência e instala
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia o restante do código
COPY . .

# Cria um usuário não-root para executar a aplicação
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Muda para o usuário não-root
USER appuser

# Expõe a porta padrão do Flask
EXPOSE 5000

# Health check para verificar se a aplicação está rodando
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/', timeout=5)" || exit 1

# Comando para iniciar a aplicação
CMD ["python", "variant_app.py"]
