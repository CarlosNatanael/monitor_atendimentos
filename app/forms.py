from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, EqualTo, ValidationError
from app.models import User, Client
from wtforms_sqlalchemy.fields import QuerySelectField

class LoginForm(FlaskForm):
    """Formulario para login de usuarios"""
    username = StringField('Usuário', validators=[DataRequired(message="Campo obrigatorio.")])
    password = PasswordField('Senha', validators=[DataRequired(message="Campo obrigatorio")])
    remember_me = BooleanField('Lembrar-me')
    submit = SubmitField('Entrar')

class RegistrationForm(FlaskForm):
    """Formulário para novos registros de novos atendentes"""
    username = StringField('Nome de Usuário', validators=[DataRequired(message="Campo obrigatorio")])
    password = PasswordField('Senha', validators=[DataRequired(message="Campo obrigatorio")])
    password2 = PasswordField(
        'Repita a Senha', validators=[DataRequired(message="Campo obrigatorio"),
                                      EqualTo('password', message='As senhas devem ser iguais.')])
    submit = SubmitField('Registrar')

    def validate_username(self, username):
        """Verifica se o nome do Usuário já existe no db."""
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Este nome de usuário já está em uso. Por favor, escolha outro.')
        
def get_clients():
    """Função helper para buscar clientes para o formulário."""
    return Client.query

class InteractionForm(FlaskForm):
    """Formulário para registrar um novo atendimento."""
    client = QuerySelectField('Cliente', query_factory=get_clients, get_label='name', allow_blank=False, validators=[DataRequired()])
    channel = SelectField('Canal', choices=[('WhatsApp', 'WhatsApp')], validators=[DataRequired()])
    category = SelectField('Categoria', choices=[
        ('Dúvida Técnica', 'Dúvida Técnica'),
        ('Suporte', 'Suporte'),
    ], validators=[DataRequired()])
    description = TextAreaField('Descrição do Atendimento', validators=[DataRequired()])
    status = SelectField('Status', choices=[('Aberto', 'Aberto'), ('Em Andamento', 'Em Andamento'), ('Resolvido', 'Resolvido'), ('Pendente', 'Pendente')], validators=[DataRequired()])
    had_anydesk_session = BooleanField('Houve acesso via AnyDesk?')
    submit_interaction = SubmitField('Registrar Atendimento')

class ClientForm(FlaskForm):
    """Formulário para registrar um novo cliente."""
    name = StringField('Nome do Cliente', validators=[DataRequired()])
    phone = StringField('Telefone (WhatsApp)', validators=[DataRequired()])
    submit_client = SubmitField('Salvar Cliente')