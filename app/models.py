from datetime  import datetime
from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class User(db.Model, UserMixin):
    """Modelo para os Usuarios do sistema"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256))
    is_supervisor = db.Column(db.Boolean, default=False, nullable=False)

    interactions = db.relationship('Interaction', backref='user', lazy='dynamic')

    def set_password(self, password):
        """Cria um hash seguro para a senha"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifica se a senha fornecida corresponde ao hash"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'
class Client(db.Model):
    """Modelo para os Clientes atendidos."""
    __tablename__ = 'clients'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False, index=True)
    phone = db.Column(db.String(40), unique=True, nullable=False)
    
    # Relação com os atendimentos: um cliente pode ter vários atendimentos
    interactions = db.relationship('Interaction', backref='client', lazy='dynamic')
    
    def __repr__(self):
        return f'<Client {self.name}>'

class Interaction(db.Model):
    """Modelo para registrar cada Atendimento."""
    __tablename__ = 'interactions'

    id = db.Column(db.Integer, primary_key=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    
    channel = db.Column(db.String(50), nullable=False) # 'WhatsApp' ou 'AnyDesk'
    had_anydesk_session = db.Column(db.Boolean, default=False) # O checkbox extra
    category = db.Column(db.String(100), nullable=False) # 'Dúvida Técnica', 'Suporte', etc.
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='Aberto', nullable=False) # 'Aberto', 'Resolvido', etc.
    
    start_time = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    end_time = db.Column(db.DateTime, nullable=True) # Preenchido ao resolver
    
    def __repr__(self):
        return f'<Interaction {self.id}>'