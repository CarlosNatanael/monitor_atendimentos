from flask import render_template, flash, redirect, url_for, request, Blueprint
from flask_login import login_user, logout_user, current_user, login_required
from app import db
from app.models import User, Client, Interaction
from app.forms import LoginForm, RegistrationForm, InteractionForm, ClientForm 

bp = Blueprint('main', __name__)

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    interaction_form = InteractionForm()
    client_form = ClientForm()

    if client_form.submit_client.data and client_form.validate_on_submit():
        new_client = Client(name=client_form.name.data, phone=client_form.phone.data)
        try:
            db.session.add(new_client)
            db.session.commit()
            flash('Cliente cadastrado com sucesso!', 'success')
        except:
            db.session.rollback()
            flash('Erro: Este telefone já está cadastrado.', 'danger')
        return redirect(url_for('main.index'))

    if interaction_form.submit_interaction.data and interaction_form.validate_on_submit():
        new_interaction = Interaction(
            user_id=current_user.id,
            client_id=interaction_form.client.data.id,
            channel=interaction_form.channel.data,
            category=interaction_form.category.data,
            description=interaction_form.description.data,
            status=interaction_form.status.data,
            had_anydesk_session=interaction_form.had_anydesk_session.data
        )
        db.session.add(new_interaction)
        db.session.commit()
        flash('Atendimento registrado com sucesso!', 'success')
        return redirect(url_for('main.index'))
    
    if current_user.is_supervisor:
        interactions = Interaction.query.order_by(Interaction.start_time.desc()).all()
    else:
        interactions = Interaction.query.filter_by(user_id=current_user.id).order_by(Interaction.start_time.desc()).all()

    return render_template('index.html', 
                           interaction_form=interaction_form, 
                           client_form=client_form, 
                           interactions=interactions)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Usuário ou senha inválidos', 'danger')
            return redirect(url_for('main.login'))
        
        login_user(user, remember=form.remember_me.data)
        flash('Login efetuado com sucesso!', 'success')
        return redirect(url_for('main.index'))
    
    return render_template('login.html', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Parabéns, você foi registrado com sucesso!', 'success')
        return redirect(url_for('main.login'))
        
    return render_template('register.html', form=form)

@bp.route('/interaction/<int:interaction_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_interaction(interaction_id):
    interaction = Interaction.query.get_or_404(interaction_id)

    # Verifica se o usuário tem permissão para editar
    if not current_user.is_supervisor and current_user.id != interaction.user_id:
        flash('Você não tem permissão para editar este atendimento.', 'danger')
        return redirect(url_for('main.index'))

    form = InteractionForm(obj=interaction) # Pré-popula o formulário com os dados do objeto

    if form.validate_on_submit():
        # Atualiza o objeto com os dados do formulário
        interaction.client = form.client.data
        interaction.channel = form.channel.data
        interaction.category = form.category.data
        interaction.description = form.description.data
        interaction.status = form.status.data
        interaction.had_anydesk_session = form.had_anydesk_session.data
        
        db.session.commit()
        flash('Atendimento atualizado com sucesso!', 'success')
        return redirect(url_for('main.index'))

    return render_template('edit_interaction.html', form=form, interaction=interaction)

@bp.route('/interaction/<int:interaction_id>/delete', methods=['POST'])
@login_required
def delete_interaction(interaction_id):
    interaction = Interaction.query.get_or_404(interaction_id)

    # Verifica se o usuário tem permissão para excluir
    if not current_user.is_supervisor and current_user.id != interaction.user_id:
        flash('Você não tem permissão para excluir este atendimento.', 'danger')
        return redirect(url_for('main.index'))

    db.session.delete(interaction)
    db.session.commit()
    flash('Atendimento excluído com sucesso!', 'success')
    return redirect(url_for('main.index'))