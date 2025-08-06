# run.py
from app import create_app, db
from app.models import User, Client, Interaction

# Cria a instância da aplicação usando nossa factory
app = create_app()

# Permite usar o terminal interativo do Flask com os modelos já importados
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Client': Client, 'Interaction': Interaction}