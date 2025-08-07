from flask import render_template, flash, redirect, url_for, request, Blueprint
from flask_login import login_user, logout_user, current_user, login_required
from app import db
from app.models import User, Interaction, InteractionHistory
from app.forms import LoginForm, RegistrationForm, InteractionForm, EditUserForm
from sqlalchemy import func
from datetime import date, datetime, time

bp = Blueprint('main', __name__)

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    interaction_form = InteractionForm()

    if interaction_form.validate_on_submit():
        new_interaction = Interaction(
            user_id=current_user.id,
            client_name=interaction_form.client_name.data, # Campo novo
            client_phone=interaction_form.client_phone.data, # Campo novo
            channel=interaction_form.channel.data,
            category=interaction_form.category.data,
            description=interaction_form.description.data,
            status=interaction_form.status.data,
            had_anydesk_session=interaction_form.had_anydesk_session.data
        )
        db.session.add(new_interaction)
        history_log = InteractionHistory(
            interaction=new_interaction,
            user_id=current_user.id,
            field_changed='status',
            old_value='N/A',
            new_value=new_interaction.status
        )
        db.session.add(history_log)

        db.session.commit() # Commit final
        flash('Atendimento registrado com sucesso!', 'success')
        return redirect(url_for('main.index'))
    
    search_date_str = request.args.get('search_date')
    if search_date_str:
        try:
            search_date_obj = date.fromisoformat(search_date_str)
        except ValueError:
            flash('Formato de data inválido.', 'danger')
            search_date_obj = date.today()
    else:
        search_date_obj = date.today()

    start_of_day = datetime.combine(search_date_obj, time.min)
    end_of_day = datetime.combine(search_date_obj, time.max)

    # Query base, agora filtrando por um intervalo de tempo
    query = Interaction.query.filter(
        Interaction.start_time >= start_of_day,
        Interaction.start_time <= end_of_day
    )

    query = query.filter_by(user_id=current_user.id)

    interactions = query.order_by(Interaction.start_time.desc()).all()

    if not current_user.is_supervisor:
        query = query.filter_by(user_id=current_user.id)
    interactions = query.order_by(Interaction.start_time.desc()).all()

    return render_template('index.html',
                           interaction_form=interaction_form,
                           interactions=interactions,
                           today=date.today().isoformat())

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
        if user.is_supervisor:
            return redirect(url_for('main.admin_dashboard'))
        else:
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

    form = InteractionForm(obj=interaction)

    if form.validate_on_submit():
        interaction.client_name = form.client_name.data
        interaction.client_phone = form.client_phone.data
        interaction.channel = form.channel.data
        interaction.category = form.category.data
        interaction.description = form.description.data
        interaction.status = form.status.data
        interaction.had_anydesk_session = form.had_anydesk_session.data

        if interaction.status != form.status.data:
            history_log = InteractionHistory(
                interaction=interaction,
                user_id=current_user.id,
                field_changed='status',
                old_value=interaction.status,
                new_value=form.status.data
            )
            db.session.add(history_log)
        
        db.session.commit()
        flash('Atendimento atualizado com sucesso!', 'success')
        return redirect(url_for('main.index'))

    return render_template('edit_interaction.html', form=form, interaction=interaction)

@bp.route('/interaction/<int:interaction_id>/delete', methods=['POST'])
@login_required
def delete_interaction(interaction_id):
    interaction = Interaction.query.get_or_404(interaction_id)

    if not current_user.is_supervisor and current_user.id != interaction.user_id:
        flash('Você não tem permissão para excluir este atendimento.', 'danger')
        return redirect(url_for('main.index'))

    db.session.delete(interaction)
    db.session.commit()
    flash('Atendimento excluído com sucesso!', 'success')
    return redirect(url_for('main.index'))

@bp.route('/interaction/<int:interaction_id>/view')
@login_required
def view_interaction(interaction_id):
    interaction = Interaction.query.get_or_404(interaction_id)

    if not current_user.is_supervisor and current_user.id != interaction.user_id:
        flash('Você não tem permissão para visualizar este atendimento.', 'danger')
        return redirect(url_for('main.index'))

    history = []
    if current_user.is_supervisor:
        history = interaction.history.order_by(InteractionHistory.timestamp.asc()).all()

    return render_template('view_interaction.html', interaction=interaction, history=history)

@bp.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_supervisor:
        flash('Acesso negado.', 'danger')
        return redirect(url_for('main.index'))

    search_date_str = request.args.get('search_date')
    if search_date_str:
        try:
            search_date_obj = date.fromisoformat(search_date_str)
        except ValueError:
            search_date_obj = date.today()
    else:
        search_date_obj = date.today()

    start_of_day = datetime.combine(search_date_obj, time.min)
    end_of_day = datetime.combine(search_date_obj, time.max)

    # --- NOVAS QUERIES ---

    # 1. Busca todos os atendimentos do dia
    interactions = Interaction.query.filter(
        Interaction.start_time >= start_of_day,
        Interaction.start_time <= end_of_day
    ).order_by(Interaction.start_time.desc()).all()

    # 2. Calcula as estatísticas por status para os cartões e para o gráfico
    status_counts = db.session.query(
        Interaction.status, func.count(Interaction.id)
    ).filter(
        Interaction.start_time >= start_of_day,
        Interaction.start_time <= end_of_day
    ).group_by(Interaction.status).all()

    # Dicionário de estatísticas para fácil acesso
    stats = {status: count for status, count in status_counts}

    # Dados para o gráfico de pizza
    chart_labels = list(stats.keys())
    chart_values = list(stats.values())

    # 3. Busca a lista de atendentes
    users = User.query.filter_by(is_supervisor=False).all()

    return render_template('admin/dashboard.html', 
                           interactions=interactions,
                           users=users,
                           stats=stats,
                           chart_labels=chart_labels,
                           chart_values=chart_values,
                           today=search_date_obj.isoformat())

@bp.route('/admin/user/<int:user_id>')
@login_required
def user_details(user_id):
    # Acesso restrito para administradores
    if not current_user.is_supervisor:
        flash('Acesso negado.', 'danger')
        return redirect(url_for('main.index'))
    user = User.query.get_or_404(user_id)
    interactions = Interaction.query.filter_by(user_id=user.id).order_by(Interaction.start_time.desc()).all()
    status_counts = db.session.query(
        Interaction.status, func.count(Interaction.id)
    ).filter(Interaction.user_id == user.id).group_by(Interaction.status).all()

    stats = {status: count for status, count in status_counts}
    stats['Total'] = sum(stats.values())

    return render_template('admin/user_details.html', user=user, interactions=interactions, stats=stats)

@bp.route('/admin/users')
@login_required
def user_management():
    if not current_user.is_supervisor:
        flash('Acesso negado.', 'danger')
        return redirect(url_for('main.index'))
    users = User.query.filter(User.id != current_user.id).all()

    return render_template('admin/user_management.html', users=users)

@bp.route('/admin/user/<int:user_id>/toggle_admin', methods=['POST'])
@login_required
def toggle_admin(user_id):
    if not current_user.is_supervisor:
        flash('Acesso negado.', 'danger')
        return redirect(url_for('main.index'))

    user_to_toggle = User.query.get_or_404(user_id)
    user_to_toggle.is_supervisor = not user_to_toggle.is_supervisor

    db.session.commit()

    if user_to_toggle.is_supervisor:
        flash(f'O usuário {user_to_toggle.username} foi promovido a administrador.', 'success')
    else:
        flash(f'O usuário {user_to_toggle.username} foi rebaixado para atendente.', 'success')

    return redirect(url_for('main.user_management'))

@bp.route('/admin/user/add', methods=['GET', 'POST'])
@login_required
def add_user():
    if not current_user.is_supervisor:
        flash('Acesso negado.', 'danger')
        return redirect(url_for('main.index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(f'O usuário {user.username} foi criado com sucesso!', 'success')
        return redirect(url_for('main.user_management'))

    return render_template('admin/add_user.html', form=form)

@bp.route('/admin/user/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if not current_user.is_supervisor:
        flash('Acesso negado.', 'danger')
        return redirect(url_for('main.index'))

    user_to_edit = User.query.get_or_404(user_id)
    form = EditUserForm(original_username=user_to_edit.username)

    if form.validate_on_submit():
        user_to_edit.username = form.username.data
        # Se o campo de senha foi preenchido, atualiza a senha.
        if form.password.data:
            user_to_edit.set_password(form.password.data)
        db.session.commit()
        flash(f'Usuário {user_to_edit.username} atualizado com sucesso!', 'success')
        return redirect(url_for('main.user_management'))
    elif request.method == 'GET':
        # Preenche o formulário com os dados atuais do usuário
        form.username.data = user_to_edit.username

    return render_template('admin/edit_user.html', form=form, user=user_to_edit)


@bp.route('/admin/user/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    # Verifica se o usuário logado é um admin
    if not current_user.is_supervisor:
        flash('Acesso negado.', 'danger')
        return redirect(url_for('main.index'))

    # Impede que o admin exclua a si mesmo
    if user_id == current_user.id:
        flash('Você não pode excluir sua própria conta de administrador.', 'danger')
        return redirect(url_for('main.user_management'))

    user_to_delete = User.query.get_or_404(user_id)

    # Antes de deletar o usuário, deleta os atendimentos associados a ele
    Interaction.query.filter_by(user_id=user_to_delete.id).delete()

    db.session.delete(user_to_delete)
    db.session.commit()

    flash(f'O usuário {user_to_delete.username} e todos os seus atendimentos foram excluídos com sucesso.', 'success')
    return redirect(url_for('main.user_management'))

@bp.route('/admin/all_interactions')
@login_required
def all_interactions():
    # Acesso restrito para administradores
    if not current_user.is_supervisor:
        flash('Acesso negado.', 'danger')
        return redirect(url_for('main.index'))

    # Busca TODOS os atendimentos, sem filtro de data, ordenados do mais novo para o mais antigo.
    interactions = Interaction.query.order_by(Interaction.start_time.desc()).all()

    return render_template('admin/all_interactions.html', interactions=interactions)

@bp.route('/admin/reports')
@login_required
def reports():
    # Acesso restrito para administradores
    if not current_user.is_supervisor:
        flash('Acesso negado.', 'danger')
        return redirect(url_for('main.index'))

    # Query 1: Atendimentos por Categoria
    category_data = db.session.query(
        Interaction.category, 
        func.count(Interaction.id)
    ).group_by(Interaction.category).order_by(func.count(Interaction.id).desc()).all()

    category_labels = [row[0] for row in category_data]
    category_values = [row[1] for row in category_data]

    # Query 2: Atendimentos por Atendente (apenas atendentes, não admins)
    agent_data = db.session.query(
        User.username,
        func.count(Interaction.id)
    ).join(Interaction, User.id == Interaction.user_id).filter(User.is_supervisor == False).group_by(User.username).order_by(func.count(Interaction.id).desc()).all()

    agent_labels = [row[0] for row in agent_data]
    agent_values = [row[1] for row in agent_data]

    return render_template(
        'admin/reports.html',
        title='Relatórios',
        category_labels=category_labels,
        category_values=category_values,
        agent_labels=agent_labels,
        agent_values=agent_values
    )