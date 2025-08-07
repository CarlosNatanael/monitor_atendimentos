from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, EqualTo, ValidationError
from app.models import User

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
        
class InteractionForm(FlaskForm):
    """Formulário para registrar um novo atendimento."""
    client_name = StringField('Nome do Cliente', validators=[DataRequired()])
    client_phone = StringField('Telefone (WhatsApp)', validators=[DataRequired()])
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

class EditUserForm(FlaskForm):
    """Formulário para editar um usuário existente."""
    username = StringField('Nome de Usuário', validators=[DataRequired()])
    # Deixamos os campos de senha opcionais. Se ficarem em branco, a senha não muda.
    password = PasswordField('Nova Senha (deixe em branco para não alterar)')
    password2 = PasswordField(
        'Repita a Nova Senha', validators=[EqualTo('password', message='As senhas devem ser iguais.')])
    submit = SubmitField('Salvar Alterações')

    def __init__(self, original_username, *args, **kwargs):
        super(EditUserForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        # Permite que o usuário mantenha seu nome original, mas verifica se o novo nome já não está em uso por outra pessoa.
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Este nome de usuário já está em uso. Por favor, escolha outro.')