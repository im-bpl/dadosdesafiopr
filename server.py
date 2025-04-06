from flask import Flask, render_template, redirect, url_for, send_from_directory
import os
from app import app as dash_app

# Criar uma aplicação Flask
server = Flask(__name__, static_folder='assets')

# Registrar o Dash app como uma rota no Flask
dash_app.server = server

@server.route('/')
def index():
    # Rota para a página inicial estática
    return send_from_directory('.', 'index.html')

@server.route('/dashboard')
def dashboard():
    # Redirecionar para o Dash app
    return redirect('/dash')

@server.route('/assets/<path:path>')
def serve_assets(path):
    # Servir arquivos estáticos
    return send_from_directory('assets', path)

@server.route('/dash')
def dash_app_route():
    # Servir o Dash app
    return dash_app.index()

if __name__ == '__main__':
    # Obter a porta do ambiente ou usar 8050 como padrão
    port = int(os.environ.get("PORT", 8050))
    server.run(host="0.0.0.0", port=port, debug=False)
