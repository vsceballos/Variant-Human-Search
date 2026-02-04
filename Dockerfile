# Usa uma imagem oficial leve do Python (Linux Debian-based)
FROM python:3.9-slim

# Define diretório de trabalho no container
WORKDIR /app

# Copia os arquivos de dependência e instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código
COPY . .

# Expõe a porta padrão do Flask
EXPOSE 5000

# Comando para iniciar a aplicação
CMD ["python", "variant_app.py"]
