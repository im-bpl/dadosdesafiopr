import os
from server import server

# Este arquivo serve como ponto de entrada para servidores WSGI como Gunicorn
# A variável 'server' é importada do módulo server.py e representa o servidor Flask
# que integra tanto a página estática quanto o Dash app

if __name__ == "__main__":
    # Este bloco é executado quando o arquivo é executado diretamente
    # Útil para testes locais
    port = int(os.environ.get("PORT", 8050))
    server.run(host="0.0.0.0", port=port, debug=False)
