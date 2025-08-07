import os
from app import create_app, db
from app.models import User
from getpass import getpass
from config import Config 

app = create_app(os.getenv('FLASK_CONFIG') or Config)

def create_admin():
    """Cria o usuário administrador inicial."""
    with app.app_context():
        print("--- Criando Conta de Administrador ---")
        username = input("Digite o nome de usuário do admin: ")

        if User.query.filter_by(username=username).first():
            print(f"Erro: O usuário '{username}' já existe.")
            return

        password = getpass("Digite a senha do admin: ")
        password2 = getpass("Confirme a senha: ")

        if password != password2:
            print("Erro: As senhas não coincidem.")
            return

        admin_user = User(username=username, is_supervisor=True)
        admin_user.set_password(password)

        db.session.add(admin_user)
        db.session.commit()
        print(f"Administrador '{username}' criado com sucesso!")

if __name__ == '__main__':
    create_admin()